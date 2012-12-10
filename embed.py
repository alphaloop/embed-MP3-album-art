#! /usr/bin/env python

import os, sys, glob, eyeD3, hashlib

CACHE_FILE_PREFIX = os.getenv("HOME") + "/.cache/media-art/album-"

def embedAlbumArt(dir = "."):
    artworkNotFoundFiles = []
    errorEmbeddingFiles = []
    noMetadataFiles = []
    mp3s = findMP3Files(dir)
    
    for mp3 in mp3s:
        print "Processing %s" % mp3

        tag = eyeD3.Tag()
        hasMetadata = tag.link(mp3)

        if not hasMetadata:
            print "No Metadata - skipping."
            noMetadataFiles.append(mp3)
            continue

        if hasEmbeddedArtwork(tag):
            print "Artwork already embedded - skipping."
            continue

        artworkFilename = findAlbumArtworkFile(tag)

        if not artworkFilename:
            print "Couldn't find artwork file - skipping."
            artworkNotFoundFiles.append(mp3)
            continue

        print "Found artwork file: %s" % (artworkFilename)

	wasEmbedded = embedArtwork(tag, artworkFilename)

        if wasEmbedded:
            print "Done.\n"
        else:
            print "Failed to embed.\n"
            errorEmbeddingFiles.append(mp3)

    if artworkNotFoundFiles:
        print "\nArtwork not found for:\n"
        print "\n".join(artworkNotFoundFiles)

    if errorEmbeddingFiles:
        print "\nError embedding artwork in:\n"
        print "\n".join(errorEmbeddingFiles)

    if noMetadataFiles:
        print "\nNo Metadata found for files:\n"
        print "\n".join(noMetadataFiles)

def findMP3Files(dir = "."):	
    mp3s = []
    mp3s.extend(glob.glob("/".join([dir, ".", "*.mp3"])))
    mp3s.extend(glob.glob("/".join([dir, "*/*", "*.mp3"])))
    mp3s.sort()
    return mp3s

def hasEmbeddedArtwork(tag):
    return len(tag.getImages())

def findAlbumArtworkFile(tag):
    key = "%s\t%s" % (tag.getArtist(), tag.getAlbum())
    md5 = getMD5Hash(key)
    filename = CACHE_FILE_PREFIX + md5 + ".jpg"
    if os.path.exists(filename):
        return filename
    else:
        return 0

def getMD5Hash(string):
    string = string.encode("utf-8")
    md5 = hashlib.md5()
    md5.update(string)
    return md5.hexdigest()

def embedArtwork(tag, artworkFilename):
    tag.addImage(eyeD3.ImageFrame.FRONT_COVER, artworkFilename)
    success = 0
    try:
        success = tag.update()
    except:
        success = 0
    return success

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Usage: %s path" % (sys.argv[0])
    else:
        embedAlbumArt(sys.argv[1])

