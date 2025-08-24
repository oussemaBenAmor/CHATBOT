from app import create_app
from threading import Thread
from app.routes import train_chatbot
import time
import threading
import logging 

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


app = create_app()

app.config['TRAINING_FOLDER'] = '/chatbot-training'

def periodic_training(interval_seconds=3600):
    def loop():
        while True:
            try:
                logging.info("Starting training...")
                train_chatbot(app.config['TRAINING_FOLDER'])
                logging.info("Training completed.")
            except Exception as e:
                logging.error(f"Training failed: {e}")
            time.sleep(interval_seconds)

    # Start background thread
    threading.Thread(target=loop, daemon=True).start()

# Start periodic training (in background)
periodic_training(interval_seconds=3600)
if __name__ == "__main__":
    app.run(debug=True, port=5050)
