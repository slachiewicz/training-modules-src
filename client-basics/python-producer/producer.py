from confluent_kafka import Producer
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.stderr.write('Usage: %s <bootstrap-brokers> <topic>\n' % sys.argv[0])
        sys.exit(1)

    brokers = sys.argv[1]
    topic = sys.argv[2]

    # Producer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    conf = {'bootstrap.servers': brokers}

    # Create Producer instance
    p = Producer(**conf)

    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).
    def delivery_callback(err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            sys.stderr.write('%% Message delivered to %s [%d] @ %d\n' %
                             (msg.topic(), msg.partition(), msg.offset()))

    # Read user input and produce to Kafka
    while True:
        try:
            key = input("enter the key for your message\n")
            value = input("enter the value for your message\n")
            p.produce(topic, key=key, value=value, callback=delivery_callback)
        except KeyboardInterrupt:
            break
        except BufferError:
            sys.stderr.write(
                '%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(p)
                )
        # Serve delivery callback queue.
        # NOTE: Since produce() is an asynchronous API this poll() call
        #       will most likely not serve the delivery callback for the
        #       last produce()d message.
        p.poll(0)

    # Wait until all messages have been delivered
    sys.stderr.write('%% Waiting for %d deliveries\n' % len(p))
    p.flush()