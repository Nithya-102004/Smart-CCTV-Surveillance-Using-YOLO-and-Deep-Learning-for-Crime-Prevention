if __name__ == "__main__":
    import os
    import requests
    from ultralytics import YOLO

    weights_path = 'yolo11n.pt'
    if not os.path.exists(weights_path):
        print(f"Downloading {weights_path} manually bypassing curl...")
        url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt"
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(weights_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
        
    model = YOLO(weights_path)
    model.train(data='datasets/data.yaml', epochs=20, imgsz=440, device=0, batch=8, amp=True)
