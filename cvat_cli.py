from cvat_client import CVATClient
import traceback
import argparse
import json
import os

def main(args):
    try:
        # Just create project
        if args.project_name and args.project_labels:
            cvat_writer = CVATClient(args.host, args.port, args.login, args.password)
            project = cvat_writer.create_project(args.project_name, args.project_labels)
            print(f'Project with ID:{project.id} is created.')

        # Creating new task
        elif args.task_name and args.images_path:
            cvat_writer = CVATClient(args.host, args.port, args.login, args.password)
        
            if args.project_id == -1:
                project = cvat_writer.get_projects()[-1]
            else:
                project = cvat_writer.get_project(args.project_id)

            images_paths = [os.path.join(args.images_path,f) for f in os.listdir(args.images_path) if '.png'in f or '.jpg' in f]
            task = cvat_writer.create_task(
                project.id, images_paths, args.task_name)

            print(f'Task with ID: {task.id} is created, {len(images_paths)} images are uploaded.')

        elif args.coco_ann_path and args.task_id!=-1:
            cvat_writer = CVATClient(args.host, args.port, args.login, args.password)
            task = cvat_writer.get_task(args.task_id)
            annotations_coco_path = args.coco_ann_path
            task.import_annotations('COCO 1.0',annotations_coco_path)

        # Add BBOX Annotations
        elif args.bbox_ann:
            cvat_writer = CVATClient(args.host, args.port, args.login, args.password)
            # Load from JSON
            with open(args.bbox_ann, 'r') as f:
                data = json.load(f)
                bboxes = data['bboxes']
                labels = data['labels']

            if args.task_id == -1:
                task = cvat_writer.get_tasks()[-1]
            else:
                task = cvat_writer.get_task(args.task_id)
            
            cvat_writer.upload_bbox(task, bboxes, labels, args.replace_ann)

        # add Polygon Annotations
        elif args.poly_ann:
            cvat_writer = CVATClient(args.host, args.port, args.login, args.password)
            # Load from JSON
            with open(args.poly_ann, 'r') as f:
                data = json.load(f)
                polygons = data['polygons']
                labels = data['labels']

            if args.task_id == -1:
                task = cvat_writer.get_tasks()[-1]
            else:
                task = cvat_writer.get_task(args.task_id)
            
            cvat_writer.upload_poly(
                task, polygons, labels, args.poly_eps, args.replace_ann)

        elif args.download:
            cvat_writer = CVATClient(args.host, args.port, args.login, args.password)
            if args.project_id == -1:
                project = cvat_writer.get_projects()[-1]
            else:
                project = cvat_writer.get_project(args.project_id)
            
            print(f'Downloading Project {project.id} into: ./project_{project.id}.zip')
            cvat_writer.download_project(
                ID=project.id,
                filepath=f'./project_{project.id}.zip',
                format_name=cvat_writer.EXPORT_FORMATS[args.export_format] # YOLO
            )
        elif args.list_export_formats:
            cvat_writer = CVATClient(args.host, args.port, args.login, args.password)
            for i, format in enumerate(cvat_writer.EXPORT_FORMATS):            
                print(f'{i}. {format}')


    except Exception as e:
            print(f'An error occurred:\n{e}')
            # This will print the full traceback
            traceback.print_exc()  
    print('Done.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connect to CVAT and manage projects and tasks.')
    
    ###
    ### LOGIN
    ###
    parser.add_argument('--host', type=str, required=True, help='CVAT server host (e.g., 10.127.0.96)')
    parser.add_argument('--port', type=str, required=True, help='CVAT server port (e.g., 8080)')
    parser.add_argument('--login', type=str, required=True, help='CVAT username for login')
    parser.add_argument('--password', type=str, required=True, help='CVAT password for login')
    
    ###
    ### General Info
    ###
    parser.add_argument('--project_name', type=str, required=False, help='Name of the project to create')
    parser.add_argument('--project_labels', type=str, nargs='+', required=False, help='Labels for the project (space-separated)')

    
    parser.add_argument('--project_id', type=int, default=-1, required=False, help='ID of the existing project (default: -1 adds to last project)')
    parser.add_argument('--images_path', type=str, required=False, help='Path to the directory containing images for the task')
    parser.add_argument('--task_name', type=str, required=False, help='Name of the task to create')

    parser.add_argument('--task_id', type=int, default=-1, required=False, help='ID of the existing task (default: -1 adds to last project)')

    parser.add_argument('--bbox_ann', type=str, required=False, help='Path to the JSON bbox annotation file')
    parser.add_argument('--poly_ann', type=str, required=False, help='Path to the JSON polygon annotation file')
    parser.add_argument('--poly_eps', type=float, default=0.9, required=False, help='Epsilon value for polygon approximation (default: 0.9). To turn off set to 0.0. Determines the maximum distance from the original curve to the approximated curve. Downsample happened only if you have more then 50 points.')
    parser.add_argument('--replace_ann', action='store_true', help='Replace the annotations (default: False)')

    parser.add_argument('--download', action='store_true', help='Download project (default: False)')
    parser.add_argument('--export_format', type=int, default=-1, required=False, help='Index of an export format')
    parser.add_argument('--list_export_formats', action='store_true', required=False, help='list of all avalable export formats')

    ###
    ### Upload COCO 1.0 annotations
    ###
    parser.add_argument('--coco_ann_path', type=str, help='path to  COCO Annotations')
    # parser.add_argument('--task_id', type=int, help='ID of the task to update')

    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the parsed arguments
    main(args)