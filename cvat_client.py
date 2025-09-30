import cv2 
import numpy as np
from cvat_sdk import make_client, models
from cvat_sdk.core.proxies.tasks import ResourceType, Task
# from cvat_sdk.core.helpers import DeferredTqdmProgressReporter

# import inspect;import pdb;pdb.set_trace() #inspect.signature


class CVATClient:
    '''
    CVAT automaticly sorting images by name so 
    make sure that all of your images sorted.
    '''
    def __init__(self, host, port, login, password):
        self.client = make_client(
            host=host, 
            port=port, 
            credentials=(login, password))

        self.client.organization_slug = 'INDSYS'

        self.EXPORT_FORMATS = self._get_valid_export_formats()

    def create_project(self, project_name, labels:list[str]):
        _labels = [{'name':l} for l in labels]
        
        project = self.client.projects.create(
            models.ProjectWriteRequest(
                name=project_name,
                labels=_labels
            ))
        return project

    def get_projects(self):
        # Get existing projects
        _projects_list = self.client.projects.list()
        _projects_list.reverse()
        return _projects_list
    def get_project(self,ID:int):
        # Get project by ID
        return self.client.projects.retrieve(ID)

    def get_project_labels(self,ID:int, show_all=False):
        # Get lebel data for a project by ID
        _labels = self.client.projects.retrieve(ID).get_labels()
        if show_all:
            return _labels
        else:
            return [{'id':d['id'],'name':d['name']} for d in _labels]

    def create_task(self, project_id:int, img_paths:list, task_name:str='GenericTask'):
        print('Creating a task, please wait...')

        task = self.client.tasks.create_from_data(
             models.TaskWriteRequest(
                name = task_name,
                project_id = project_id
            ),
            resource_type = ResourceType.LOCAL,
            resources=img_paths,
        )
        return task

    def get_tasks(self):
        # Get existing tasks
        _task_list = self.client.tasks.list()
        _task_list.reverse()
        return _task_list
    def get_task(self, ID:int):
        # Get task by ID
        return self.client.tasks.retrieve(ID)

    def upload_coco_to_task(self):
        pass

    def upload_bbox(self, task:Task, bboxes:dict, labels:dict, replace_existing_ann=False):
        """
        bboxes: dict, we assume dict with id that match image ids 
            {0:[[1,2,3,4],[1,2,3,4]],...}
        labels: dict, we assume dict with id that match image ids  
            {0:['shram','raskrytie'],...}  
        """
        # import inspect;import pdb;pdb.set_trace() #inspect.signature
        task_labels = task.get_labels()
        task_labels_id_by_name = {label.name: label.id for label in task_labels}

        # TODO:check if labels are correct 

        all_shapes = []
        for image_id, value in bboxes.items():
            image_boxes = bboxes[image_id]
            image_labels = labels[image_id]
            image_id = int(image_id)
            
            for i in range(len(image_boxes)):
                labelid = task_labels_id_by_name[image_labels[i]]
                points = image_boxes[i]
    
                shape = models.LabeledShapeRequest(
                    frame = image_id,
                    label_id = labelid,
                    type = "rectangle",
                    points = points,
                    source='AUTO',
                )
                all_shapes.append(shape)

        # cleaning old annotations 
        if replace_existing_ann and len(task.get_annotations()['shapes']) != 0:
            print('Removing old annotations...')
            task.remove_annotations()

        # This function adds annotations
        task.update_annotations(
            models.PatchedLabeledDataRequest(
                shapes=all_shapes,
        ))
        print(f'Uploaded {len(all_shapes)} annotations to task: {task.id}')

    def upload_poly(self, task:Task, polygons:dict, labels:dict, eps:float, replace_existing_ann=False):
        task_labels = task.get_labels()
        task_labels_id_by_name = {label.name: label.id for label in task_labels}

        all_shapes = []
        for image_id, value in polygons.items():
            image_poly = polygons[image_id]
            image_labels = labels[image_id]
            image_id = int(image_id)
            
            for i in range(len(image_poly)):
                labelid = task_labels_id_by_name[image_labels[i]]
                points = image_poly[i]
                if eps > 0:
                    old_size = len(points)/2
                    if old_size > 50:
                        points = self.downsample_poly(points)
                        print(f'Dowsample poly from {old_size} to {len(points)/2}')
    
                shape = models.LabeledShapeRequest(
                    frame = image_id,
                    label_id = labelid,
                    type = "polygon",
                    points = points,
                    source='AUTO',
                )
                all_shapes.append(shape)

        # cleaning old annotations 
        if replace_existing_ann and len(task.get_annotations()['shapes']) != 0:
            print('Removing old annotations...')
            task.remove_annotations()

        # This function adds annotations
        task.update_annotations(
            models.PatchedLabeledDataRequest(
                shapes=all_shapes,
        ))
        print(f'Uploaded {len(all_shapes)} annotations to task: {task.id}')

    def downsample_poly(self, polygon, eps:float=0.9):
        polygon = self._xy_to_stack(polygon)
        poly = cv2.approxPolyDP(polygon, eps, True)
        return self._xy_to_list(poly[:,0])

    def _xy_to_list(self,poly_stack):
        # poly_stack.shape : np.array(N,2) where [[x,y],[x,y]]
        return [int(p) for coords in poly_stack for p  in coords]

    def _xy_to_stack(self,poly_list):
        # poly_list : [x,y,x,y,x,y,x,y,...]
        polygon = np.array(poly_list)
        return np.array(list(zip(polygon[::2], polygon[1::2])))

    def _get_valid_export_formats(self):
        return [
            "CamVid 1.0",
            "Cityscapes 1.0",
            "COCO 1.0",
            "COCO Keypoints 1.0",
            "CVAT for images 1.1",
            "CVAT for video 1.1",
            "Datumaro 1.0",
            "ICDAR Localization 1.0",
            "ICDAR Recognition 1.0",
            "ICDAR Segmentation 1.0",
            "ImageNet 1.0",
            "KITTI 1.0",
            "LabelMe 3.0",
            "LFW 1.0",
            "Market-1501 1.0",
            "MOT 1.1",
            "MOTS PNG 1.0",
            "Open Images V6 1.0",
            "PASCAL VOC 1.1",
            "Segmentation mask 1.1",
            "Ultralytics YOLO Classification 1.0",
            "Ultralytics YOLO Detection 1.0",
            "Ultralytics YOLO Detection Track 1.0",
            "Ultralytics YOLO Oriented Bounding Boxes 1.0",
            "Ultralytics YOLO Pose 1.0",
            "Ultralytics YOLO Segmentation 1.0",
            "VGGFace2 1.0",
            "WiderFace 1.0",
            "YOLO 1.1"
        ]

    def download_project(self, ID:int, filepath:str, format_name:str=None):
        if format_name is None:
            format_name = self.EXPORT_FORMATS[-1] # Default to YOLO

        if format_name not in self.EXPORT_FORMATS:
            raise TypeError('Wrong export type')

        self.get_project(ID).export_dataset(format_name, filepath)


    