FROM centos:7

# Evita prompts interactivos
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Actualizar mirros
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-Base.repo && \
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-Base.repo

# Instalar dependencias del sistema
RUN yum -y update && yum install -y \
    gcc \
    gcc-c++ \
    openssl-devel \
    bzip2-devel \
    libffi-devel \
    zlib-devel \
    wget \
    make \
    curl \
    tar \
    which && \
    yum clean all

# Instalar Python 3
RUN yum install -y \
    python3 \
    python36-devel && \
    yum clean all



# Crear directorio de la app
WORKDIR /app

# Copiar tu código al contenedor
COPY . /app

# (Opcional) instalar dependencias si tienes requirements.txt
RUN if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi
