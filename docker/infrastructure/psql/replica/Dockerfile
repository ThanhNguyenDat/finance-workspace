ARG POSTGRES_VERSION=15

FROM postgres:${POSTGRES_VERSION}

ENV PGUSER=replicator
ENV PGPASSWORD=replicator_password

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod 777 /docker-entrypoint.sh

ENTRYPOINT [ "/docker-entrypoint.sh" ]
