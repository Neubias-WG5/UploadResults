import sys, os
from subprocess import call

from cytomine.models import Job

from biaflows import CLASS_OBJSEG
from biaflows.helpers import BiaflowsJob, upload_data, upload_metrics, prepare_data


def main(argv):
    # 0. Initialize Cytomine client and job if necessary and parse inputs
    with BiaflowsJob.from_cli(argv) as nj:
        nj.job.update(status=Job.RUNNING, progress=0, statusComment="Initialisation...")

        problem_cls = CLASS_OBJSEG
        is_2d = True
         
        nj.flags["do_download"] = True
        
        in_images, gt_images, in_path, gt_path, out_path, tmp_path = prepare_data(problem_cls, nj, **nj.flags)
        
        print(type(in_images[0]))
        
        # 4. Upload the annotation and labels to Cytomine
        upload_data(problem_cls, nj, in_images, out_path, **nj.flags, is_2d=is_2d, monitor_params={
            "start": 60, "end": 90, "period": 0.1
        })

        # 5. Compute and upload the metrics
        nj.job.update(progress=90, statusComment="Computing and uploading metrics...")
        upload_metrics(problem_cls, nj, in_images, gt_path, out_path, tmp_path, **nj.flags)

        # 6. End
        nj.job.update(status=Job.TERMINATED, progress=100, statusComment="Finished.")


if __name__ == "__main__":
    main(sys.argv[1:])
