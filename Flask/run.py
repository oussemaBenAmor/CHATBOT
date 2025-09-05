from app import create_app
from threading import Thread
from app.routes import train_chatbot
import time
import threading
import logging 
import datetime


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


app = create_app()

app.config['TRAINING_FOLDER'] = '/chatbot-training'




def periodic_training():
    def loop():
        while True:
            now = datetime.datetime.now()
            # Monday is 0 (0=Monday, 6=Sunday)
            if now.weekday() == 0 and now.hour == 9 and now.minute == 0:
                try:
                    logging.info("Starting training...")
                    train_chatbot(app.config['TRAINING_FOLDER'])
                    logging.info("Training completed.")
                except Exception as e:
                    logging.error(f"Training failed: {e}")
                # Sleep 61s to avoid running multiple times within the same minute
                time.sleep(61)
            else:
                # Check every 30 seconds
                time.sleep(30)

    threading.Thread(target=loop, daemon=True).start()

# Start background training loop
periodic_training()
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=5050)
