from collections import defaultdict
import os
import pika
import json

def rank_llms(llms):
    metrics = defaultdict(list)
    
    for llm in llms:
        metrics[llm.llm_name].append(llm.value)
    
    # Calculate mean of values for each LLM
    avg_metrics = {llm: sum(values)/len(values) for llm, values in metrics.items()}
    
    # Rank by mean values
    ranked_llms = sorted(avg_metrics.items(), key=lambda x: x[1])
    
    return ranked_llms

rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
rabbitmq_queue = "tasks"

def send_to_queue(task_data):
    """Send any task to RabbitMQ."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue, durable=True)

    # Send task to RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key=rabbitmq_queue,
        body=json.dumps(task_data),
        properties=pika.BasicProperties(delivery_mode=2),  # Make message persistent
    )
    connection.close()


def queue_task(task_data):
    """
    Accept any task  and send it to the RabbitMQ queue.
    The task_data should contain the task name and its parameters.
    {
        "task": "simulate_data",
        "params": {}
    }
    """
    send_to_queue(task_data)
    print(f"Message: Task {task_data['task']} has been queued")