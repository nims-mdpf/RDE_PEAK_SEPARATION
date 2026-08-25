#!/bin/bash

container_name=$(docker ps --format '{{.Names}}' | head -n 1)
docker_name_compile="rdecontreg.azurecr.io/nims/mdpf_shared/nims_mdpf_shared_peak_separation:v1.0.0.make"
docker_name="rdecontreg.azurecr.io/nims/mdpf_shared/nims_mdpf_shared_peak_separation:v1.0.0"

case "$1" in

  # model_type: convolution_voigt  (tasksupport, invoice, inputdataをコンテナに送り込む)
  push_conv)
    # docker
    docker exec $container_name mkdir -p /app/data/tasksupport
    docker exec $container_name mkdir -p /app/data/invoice
    docker exec $container_name mkdir -p /app/data/inputdata

    # tasksupport
    docker cp ../templates/template/tasksupport/invoice.schema.json $container_name:/app/data/tasksupport/
    docker cp ../templates/template/tasksupport/metadata-def.json $container_name:/app/data/tasksupport/
    docker cp ../templates/template/tasksupport/rdeconfig.yaml $container_name:/app/data/tasksupport/

    # data
    docker cp ../inputdata/case1/invoice/invoice.json $container_name:/app/data/invoice/
    docker cp ../inputdata/case1/inputdata/XPS_PMMA_C1s_Al.csv $container_name:/app/data/inputdata/
    ;;

  # model_type: pseudo_voigt  (tasksupport, invoice, inputdataをコンテナに送り込む)
  push_ps)
    # docker
    docker exec $container_name mkdir -p /app/data/tasksupport
    docker exec $container_name mkdir -p /app/data/invoice
    docker exec $container_name mkdir -p /app/data/inputdata

    # tasksupport
    docker cp ../templates/template/tasksupport/invoice.schema.json $container_name:/app/data/tasksupport/
    docker cp ../templates/template/tasksupport/metadata-def.json $container_name:/app/data/tasksupport/
    docker cp ../templates/template/tasksupport/rdeconfig.yaml $container_name:/app/data/tasksupport/

    # data
    docker cp ../inputdata/case2/invoice/invoice.json $container_name:/app/data/invoice/
    docker cp ../inputdata/case2/inputdata/XPS_PMMA_C1s_Al.csv $container_name:/app/data/inputdata/
    ;;

  # コンテナ上でコンパイルし出力されたexeを、ローカルに引き込む (解析プログラム分離の為の苦肉の策)
  pull_exe)
    print $container_name
    docker cp $container_name:/app/packages/convolution_voigt packages/.
    ;;

  # コンテナで実行し出力されたデータを、ローカルに引き込む (で確認する)
  pull_data)
    docker cp $container_name:/app/data ../.
    ;;

  # dockerをrun (コンテナを取り出す為だけに起動する)
  run_compile)
    docker run --rm -it $docker_name_compile
    ;;

  # dockerをrun (デバック用。ポート(5678(暫定))を指定する)
  run)
    docker run --rm -it -p 5678:5678 $docker_name
    ;;

  *)
    echo "Usage: $0 {push_conv|push_ps|pull_exe|push_data|run_compile|run}"
    ;;

esac
exit 0
