# Dockerfile
FROM python:3.11-alpine3.22

# Metadata
LABEL maintainer="adaptive-software"
LABEL description="Software Auto-Adattivo con Server Telnet"
LABEL version="2.0.0"

# Imposta variabili d'ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ARG PASSWORD=password
# Installing the openssh and bash package, removing the apk cache
RUN apk --update add --no-cache openssh bash \
  && sed -i s/#PermitRootLogin.*/PermitRootLogin\ yes/ /etc/ssh/sshd_config \
  && echo "root:${PASSWORD}" | chpasswd \
  && rm -rf /var/cache/apk/*
# Defining the Port 22 for service
RUN sed -ie 's/#Port 22/Port 22/g' /etc/ssh/sshd_config
RUN /usr/bin/ssh-keygen -A
RUN ssh-keygen -t rsa -b 4096 -f  /etc/ssh/ssh_host_key
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
EXPOSE 22


# Installa dipendenze Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Crea directory di lavoro
WORKDIR /agent



COPY agent0.sh /agent/agent0.sh
RUN chmod +x /agent/agent0.sh

# Imposta agent0.sh come shell di login per root
RUN sed -i 's|root:x:0:0:root:/root:/bin/ash|root:x:0:0:root:/root:/agent/agent0.sh|' /etc/passwd
RUN echo "ForceCommand /agent/agent0.sh" >> /etc/ssh/sshd_config
RUN echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config


# Punto di ingresso predefinito
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/sbin/sshd", "-D"]

