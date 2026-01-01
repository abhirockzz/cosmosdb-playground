FROM mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator:vnext-preview

# Install Python 3 and Azure Cosmos SDK
USER root
RUN tdnf update -y && \
    tdnf install -y python3 python3-pip && \
    pip3 install azure-cosmos --break-system-packages && \
    tdnf clean all

# Copy the query helper script and wrapper
COPY query.py /usr/local/bin/query.py
COPY wrapper.sh /usr/local/bin/wrapper.sh
RUN chmod +x /usr/local/bin/query.py && chmod +x /usr/local/bin/wrapper.sh

# Switch back to the default user
USER cosmosdev

# Expose ports (8081 for Cosmos, 8080 for health)
EXPOSE 8081 8080

# We inherit the ENTRYPOINT from the base image to start the emulator
