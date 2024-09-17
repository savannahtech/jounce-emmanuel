import json
import os
import pika
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from database import get_db
from tenacity import retry, wait_fixed, stop_after_attempt
from main import simulate_data, get_ranked_llms

# RabbitMQ connection parameters
rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_queue = "tasks"


# Abstraction for task execution
class Task(ABC):
    @abstractmethod
    def execute(self, db: Session, params: dict):
        """Execute the task."""
        pass


class SimulateDataTask(Task):
    def execute(self, db: Session, params: dict):
        print("Executing Simulate Data Task")
        simulate_data(db)


class RankLLMTask(Task):
    def execute(self, db: Session, params: dict):
        metric_name = params.get('metric_name')
        print(f"Executing Rank LLMs Task for metric {metric_name}")
        get_ranked_llms(db, metric_name)


# TaskFactory to map task names to their classes (OCP)
class TaskFactory:
    _task_mapping = {
        "simulate_data": SimulateDataTask,
        "rank_llms": RankLLMTask,
    }

    @staticmethod
    def get_task(task_name: str) -> Task:
        task_class = TaskFactory._task_mapping.get(task_name)
        if not task_class:
            raise ValueError(f"Unknown task: {task_name}")
        return task_class()


# Task executor (SRP, DIP)
class TaskExecutor:
    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    def execute_task(self, task_name: str, db: Session, params: dict):
        task = TaskFactory.get_task(task_name)
        task.execute(db, params)


# RabbitMQ handler (SRP, DIP)
class RabbitMQConsumer:
    def __init__(self, host, queue, task_executor: TaskExecutor):
        self.host = host
        self.queue = queue
        self.task_executor = task_executor

    def process_task(self, ch, method, properties, body):
        """Process a task from the RabbitMQ queue."""
        db = get_db().__next__()
        message = body.decode('utf-8')
        task_data = json.loads(message)
        task_name = task_data['task']
        params = task_data.get('params', {})

        try:
            self.task_executor.execute_task(task_name, db, params)
            print(f"Task {task_name} processed successfully")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing task {task_name}: {e}")

    def consume_queue(self):
        """Consume tasks from RabbitMQ."""
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)

        channel.basic_qos(prefetch_count=1)  # Fair dispatch
        channel.basic_consume(queue=self.queue, on_message_callback=self.process_task)

        print("Waiting for tasks. To exit, press CTRL+C")
        channel.start_consuming()


# Main entry point 
if __name__ == "__main__":
    task_executor = TaskExecutor()
    rabbitmq_consumer = RabbitMQConsumer(rabbitmq_host, rabbitmq_queue, task_executor)
    rabbitmq_consumer.consume_queue()
