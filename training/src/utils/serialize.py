'''
Created on Feb 4, 2015

@author: vfeng
'''

import sys
import pickle
import cPickle
#import sPickle

def saveData(myobject, filename):
    fo = open(filename , "wb")
    #print 'Saved serialized file to %s' % os.path.join(where, filename + suffix)
    cPickle.dump(myobject, fo, protocol = cPickle.HIGHEST_PROTOCOL)
    #p = cPickle.Pickler(fo) 
    #p.fast = True
    #p.dump(myobject)
    #sPickle.s_dump(myobject, fo)
    
    fo.close()

def loadData(filename):
    data_file = filename
    try:
        fo = open(data_file, "rb")
    except IOError:
        print "Couldn't open data file: %s" % data_file
        return
    try:
        #myobject = sPickle.s_load(fo)
        myobject = pickle.load(fo)
    except:
        fo.close()
        print "Unexpected error:", sys.exc_info()[0]
        raise
    fo.close()
    return myobject
