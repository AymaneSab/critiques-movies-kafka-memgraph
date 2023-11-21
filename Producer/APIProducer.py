import sys
import os
import json
import logging
import time
from datetime import datetime 
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic
from datetime import datetime


# Import Real-Time-Movie-Recommendation-System Folder Relative Path
sys.path.append('/home/hadoop/Real-Time-Movie-Recommendation-System') 

# Set up Loggin Function
def setup_producer_logging():

    log_directory = "Log/Producer_Log_Files"
    os.makedirs(log_directory, exist_ok=True)

    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
    log_filepath = os.path.join(log_directory, log_filename)

    logging.basicConfig(filename=log_filepath, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    producer_logger = logging.getLogger(__name__)  

    return producer_logger

def create_kafka_topic(topic, admin_client, producer_logger):
    try:
        topic_spec = NewTopic(topic, num_partitions=1, replication_factor=1)

        admin_client.create_topics([topic_spec])

        separator = '-' * 30
        producer_logger.info(f"{topic} {separator} Created Successfully: ")

    except Exception as e:
        error_message = "Error creating Kafka topic: " + str(e)
        producer_logger.error(error_message)

def produce_to_Topics(movieTopic, reviewTopic, producer_logger):
    try:
        producer = Producer({"bootstrap.servers": "localhost:9092"})  # Kafka broker address

        # Generate movie data
        movies_generator = get_movies()

        while True:
            # Fetch the next movie data
            movie_data = next(movies_generator)

            movie_json = json.loads(movie_data)

            # Check if "release_date" is present and not null in the movie object
            try:
                # Produce to the movies topic
                producer.produce(topic, key="movie", value=json.dumps(movie_json["movie"]))
                producer_logger.info(f"Movie Produced Successfully to {topic}: ")

                # Flush only if everything is successful
                producer.flush()

            except ValueError as ve:
                # Log the error if the date formatting fails
                error_message = f"Error formatting release date: {ve}"
                producer_logger.error(error_message)

            except Exception as ex:
                # Log other validation errors
                error_message = f"Error validating Kafka message: {ex}"
                producer_logger.error(error_message)

            # Add a delay to control the rate of data production
            time.sleep(2)

    except StopIteration:
        producer_logger.info("Movie data generator exhausted. Stopping Kafka Producer.")

    except Exception as e:
        error_message = "Error producing to Kafka: " + str(e)
        producer_logger.error(error_message)

def runKafkaProducer(topic):
    
    producer_logger = setup_producer_logging()

    try:
        producer_logger.info("Kafka Producer started.")

        # Create a Kafka admin client
        admin_client = AdminClient({"bootstrap.servers": "localhost:9092"})

        # Check if the topics exist, and create them if not
        for topic in [topic]:
            existing_topics = admin_client.list_topics().topics
            if topic not in existing_topics:
                create_kafka_topic(topic, admin_client, producer_logger)

        # Start producing to both topics simultaneously
        produce_to_Topics(topic, producer_logger)

        
    except KeyboardInterrupt:
        producer_logger.info("Kafka Producer Stopped")

    except Exception as e:
        error_message = "An unexpected error occurred in Kafka Producer: " + str(e)
        producer_logger.error(error_message)

topic = "Reviews"

runKafkaProducer(topic)
