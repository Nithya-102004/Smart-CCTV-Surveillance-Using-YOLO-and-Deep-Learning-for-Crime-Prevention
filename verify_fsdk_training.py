from fsdk_utils import train_fsdk
import fsdk
from fsdk import FSDK
import os

def verify():
    test_image = "static/user/Anna.jpg"
    test_user = "Anna_Test"
    
    if not os.path.exists(test_image):
        print(f"Test image {test_image} not found.")
        return

    print(f"--- Training FSDK with {test_user} ---")
    success = train_fsdk(test_image, test_user)
    
    if success:
        print("Training successful. Now verifying recognition...")
        
        # Now try to recognize it using a fresh tracker load
        FSDK.ActivateLibrary("fVrFCzYC5wOtEVspKM/zfLWVcSIZA4RNqx74s+QngdvRiCC7z7MHlSf2w3+OUyAZkTFeD4kSpfVPcRVIqAKWUZzJG975b/P4HNNzpl11edXGIyGrTO/DImoZksDSRs6wktvgr8lnNCB5IukIPV5j/jBKlgL5aqiwSfyCR8UdC9s=")
        FSDK.Initialize()
        
        tracker = FSDK.Tracker.FromFile("tracker70.dat")
        img = FSDK.Image(test_image)
        
        ids = tracker.FeedFrame(0, img)
        if ids:
            name = tracker.GetName(ids[0])
            print(f"Recognized face name: {name}")
            if name == test_user:
                print("VERIFICATION SUCCESS: Face correctly recognized!")
            else:
                print(f"VERIFICATION FAILURE: Recognized as '{name}' instead of '{test_user}'")
        else:
            print("VERIFICATION FAILURE: No face detected during verification.")
            
        tracker.Free()
        img.Free()
    else:
        print("Training failed.")

if __name__ == "__main__":
    verify()
