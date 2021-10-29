FROM rabbitmq:3.8-management

RUN rabbitmq-plugins enable rabbitmq_stomp
RUN rabbitmq-plugins enable rabbitmq_web_stomp
RUN rabbitmq-plugins enable rabbitmq_web_mqtt

EXPOSE 15672
EXPOSE 15674
EXPOSE 15675
EXPOSE 5672