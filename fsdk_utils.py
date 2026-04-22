import fsdk
from fsdk import FSDK
import os
import time

# License key from LiveRecognition2.py
license_key = "fVrFCzYC5wOtEVspKM/zfLWVcSIZA4RNqx74s+QngdvRiCC7z7MHlSf2w3+OUyAZkTFeD4kSpfVPcRVIqAKWUZzJG975b/P4HNNzpl11edXGIyGrTO/DImoZksDSRs6wktvgr8lnNCB5IukIPV5j/jBKlgL5aqiwSfyCR8UdC9s="

_fsdk_initialized = False

def init_fsdk():
    global _fsdk_initialized
    if not _fsdk_initialized:
        try:
            FSDK.ActivateLibrary(license_key)
            FSDK.Initialize()
            _fsdk_initialized = True
            print("FSDK initialized successfully for training.")
        except Exception as e:
            print(f"FSDK initialization error: {e}")
            return False
    return True

def train_fsdk(image_path, username):
    """
    Trains the FSDK tracker using a static image file.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return False

    if not init_fsdk():
        return False

    tracker_file = "tracker70.dat"
    tracker = None
    img = None
    
    try:
        if os.path.exists(tracker_file):
            tracker = FSDK.Tracker.FromFile(tracker_file)
        else:
            tracker = FSDK.Tracker()
            
        tracker.SetParameters(
            RecognizeFaces=True, DetectFacialFeatures=True,
            HandleArbitraryRotations=True, DetermineFaceRotationAngle=False,
            InternalResizeWidth=256, FaceDetectionThreshold=5
        )
        
        img = FSDK.Image(image_path)
        
        # Feed the frame multiple times to ensure the tracker "sees" and "learns" the face
        # For a static image, the tracker needs to detect the face and assign it a name.
        found = False
        for i in range(10):
            ids = tracker.FeedFrame(0, img)
            if ids:
                tracker.SetName(ids[0], username)
                print(f"Successfully trained face for '{username}' from {image_path} (ID: {ids[0]})")
                found = True
                break
            time.sleep(0.1)
            
        if not found:
            print(f"Warning: No face detected in {image_path} for user {username}")
        
        tracker.SaveToFile(tracker_file)
        return found
    except Exception as e:
        print(f"Error during FSDK training for {username}: {e}")
        return False
    finally:
        if tracker:
            tracker.Free()
        if img:
            img.Free()
