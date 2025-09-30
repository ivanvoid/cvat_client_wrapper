# CVAT Client Script Documentation
## Overview
This script demonstrates how to connect to the CVAT (Computer Vision Annotation Tool) server, create projects and tasks, upload annotations, and download datasets using the cvat_client library.

Module works under:
```
source cvatenv/bin/activate
```

## Functionality
### 1. Create new project
```shell
python cvat_cli.py --host 10.127.0.96 --port 8080 --login cvat_test --password QWERTY123q --project_name "My New CVAT Project" --project_labels car1 cat2 dog3
```
### 2. Create new task in existing project
```shell
python cvat_cli.py --host 10.127.0.96 --port 8080 --login cvat_test --password QWERTY123q --task_name "My New BBOX Task" --images_path ./test_imgs 
```
Specify `--project_id` to add to specific project, leave to add to last created project.
### 3. Upload BBOX Annotations
```
python cvat_cli.py --host 10.127.0.96 --port 8080 --login cvat_test --password QWERTY123q --bbox_ann bbox_labels.json --replace_ann
```
Specify `--task_id` to add to specific task, leave to add to last created task.  
Use `--replace_ann` to replace annotations that alerady exits in CVAT.
### 4. Upload Polygon Annotations
```
python cvat_cli.py --host 10.127.0.96 --port 8080 --login cvat_test --password QWERTY123q --poly_ann poly_labels.json
```
Specify `--task_id` to add to specific task, leave to add to last created task.  
Use `--replace_ann` to replace annotations that alerady exits in CVAT.

### 6. List all avalable download formats for datasets
```
python cvat_cli.py --host 10.127.0.96 --port 8080 --login cvat_test --password QWERTY123q --list_export_formats
```

### 6. Download Project as dataset
```
python cvat_cli.py --host 10.127.0.96 --port 8080 --login cvat_test --password QWERTY123q --download --export_format 25
```
Specify `--project_id` to download specific project, leave to download last created project.

### 7. Upload COCO 1.0
```
python cvat_cli.py --host 10.127.0.146 --port 8080 --login cvat_test --password QWERTY123q --coco_ann_path t89.json --task_id 89
```


### Notes
CVAT automaticly sorting images by name so make sure that all of your images sorted.
