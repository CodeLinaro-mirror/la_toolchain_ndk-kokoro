#!/bin/sh
set -e
set -x

top=$(cd $(dirname $0)/../.. && pwd)
docker_dir=$1
entry_point=$2


# On Linux, enter the Docker container before invoking the entry point.  If running in a Kokoro
# instances build this script may be run from inside a Docker container, but with the host
# docker.sock mounted to allow creating sibling containers.  In that case, use Kokoro's
# environment variables to translate the in-container paths back to the host paths necessary
# to create the sibling container.
if [ "$(uname)" == "Linux" -a "$SKIP_DOCKER" == "" ]; then
    if [ -n "${KOKORO_HOST_ROOT_DIR}" ]; then
        host_top=${KOKORO_HOST_ROOT_DIR}/${top#"${KOKORO_ROOT_DIR}"}
    else
        host_top=$top
    fi
    container_build_root=/build
    entry_point_in_container=${container_build_root}/${entry_point#"${top}"}
    docker_image=ndk-kokoro
    docker build --network=host -t $docker_image $docker_dir
    export SKIP_DOCKER=1
    docker run -v$host_top:$container_build_root -eKOKORO_BUILD_ID -eSKIP_DOCKER \
      --entrypoint $entry_point_in_container \
      $docker_image
    exit $?
fi

$entry_point
