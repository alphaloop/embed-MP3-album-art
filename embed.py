#! /usr/bin/env python

import os, sys, glob, eyed3, hashlib
import musicbrainzngs as mb
import Image

CACHE_FILE_PREFIX = '/tmp/embed'
IMAGE_SIZE = 300, 300

def embedAlbumArt(directory = '.'):
    artworkNotFoundFiles = []
    artworkNotFoundHashes = []
    errorEmbeddingFiles = []
    noMetadataFiles = []
    processedCount = 0
    embeddedCount = 0
    downloadedCount = 0
    
    initialise()
    mp3s = findMP3Files(directory)
    
    for mp3 in mp3s:
        print "Processing %s" % mp3
        processedCount = processedCount + 1

        tag = eyed3.load(mp3).tag

        if not tag:
            print("No Metadata - skipping.")
            noMetadataFiles.append(mp3)
            continue

        if hasEmbeddedArtwork(tag):
            print("Artwork already embedded - skipping.")
            continue
        
        tagHash = getMD5Hash(tag)
        if not contains(artworkNotFoundHashes, tagHash):
            artworkFilename = getCacheFilename(tag)
            if not os.path.exists(artworkFilename):
                try:
                    downloadAndCacheArtworkFile(tag)
                    downloadedCount = downloadedCount + 1
                except:
                    artworkFilename = None

        if not artworkFilename:
            print("Couldn't find artwork - skipping.")
            artworkNotFoundFiles.append(mp3)
            artworkNotFoundHashes.append(tagHash)
            continue

        print("Found artwork, embedding.")

        try:
            embedArtwork(tag, artworkFilename)
            embeddedCount = embeddedCount + 1
            print("Done.\n")
        except:
            print("Failed to embed.\n")
            errorEmbeddingFiles.append(mp3)

    if artworkNotFoundFiles:
        print("\nArtwork not found for:")
        print("\n".join(artworkNotFoundFiles))

    if errorEmbeddingFiles:
        print("\nError embedding artwork in:")
        print("\n".join(errorEmbeddingFiles))

    if noMetadataFiles:
        print("\nNo Metadata found for files:")
        print("\n".join(noMetadataFiles))
    
    print("\nProcessed %d files" % processedCount)
    print("Downloaded %d new covers" % downloadedCount)
    print("Embedded artwork into %d files" % embeddedCount)

def initialise():
    mb.set_useragent('Embed MP3 Cover Art', '1.0.0', 'https://github.com/alphaloop/embed-MP3-album-art')
    if not os.path.exists(CACHE_FILE_PREFIX):
        os.mkdir(CACHE_FILE_PREFIX)

def findMP3Files(directory = '.'):	
    mp3s = []
    mp3s.extend(glob.glob('/'.join([directory, '.', '*.mp3'])))
    mp3s.extend(glob.glob('/'.join([directory, '*/*', '*.mp3'])))
    mp3s.sort()
    return mp3s

def hasEmbeddedArtwork(tag):
    return len(tag.images)
    
def downloadAndCacheArtworkFile(tag):
    album = tag.album
    artist = tag.artist
    print("Attempting to download cover for %s %s..." % (album, artist))

    result = mb.search_releases(artist=tag.artist, release=tag.album, type='album', format='cd', strict=True)
    result = result['release-list']
    
    if len(result) == 0:
        raise "Couldn't find entry for %s %s" % (album, artist)
    
    mbid = result[0]['id']
    cover = None
    try:
        cover = mb.get_image_front(mbid)
    except:
        raise "Couldn't find artwork for %s %s" % (album, artist)
    
    filename = getCacheFilename(tag)
    f = open(filename, 'wb')
    f.write(cover)
    f.close()
    
    print("Downloaded.")
    
    resizeImage(filename)

    print("Resized.")
    
    return filename

def resizeImage(filename):
    image = Image.open(filename)
    image.thumbnail(IMAGE_SIZE)
    image.save(filename, 'JPEG')

def getCacheFilename(tag):
    md5 = getMD5Hash(tag)
    filename = CACHE_FILE_PREFIX + '/' + md5 + '.jpg'
    return filename

def getMD5Hash(tag):
    key = '%s\t%s' % (tag.artist, tag.album)
    key = key.encode('utf-8')
    md5 = hashlib.md5()
    md5.update(key)
    return md5.hexdigest()

def embedArtwork(tag, artworkFilename):
    fp = open(artworkFilename, 'rb')
    imageData = fp.read()
    fp.close()
    tag.images.set(eyed3.id3.frames.ImageFrame.FRONT_COVER, imageData, 'image/jpeg')
    tag.save()

def contains(aList, value):
    try:
        aList.index(value)
        return True
    except:
        return False

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: %s path" % (sys.argv[0]))
    else:
        embedAlbumArt(sys.argv[1])

