#!/bin/bash
#SBATCH -Jcgcnn_vn                                  # Job name
#SBATCH -Agts-vfung3                                # Charge account
#SBATCH -N1 --gres=gpu:A100:1                       # Number of nodes and GPUs required
#SBATCH --mem-per-gpu=80G                           # Memory per gpu
#SBATCH -t12:00:00                                        # Duration of the job (Ex: 15 mins)
#SBATCH -qinferno                                   # QOS name
#SBATCH -ocgcnn_job-%j.out                             # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL                  # Mail preferences
#SBATCH --mail-user=sidharth.baskaran@gatech.edu            # e-mail address for notifications

cd /storage/home/hcoda1/9/sbaskaran31/p-vfung3-0/MatDeepLearn_dev/scripts
conda activate matdeeplearn

python main.py --config_path="/nethome/sbaskaran31/projects/Sidharth/MatDeepLearn_dev/configs/examples/cgcnn_vn_hg/config_cgcnn_vn_hg.yml" \
    --run_mode="train" \
    --use_wandb=True