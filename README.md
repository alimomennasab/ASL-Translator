# Live ASL translation
*Ali Momennasab, Ramsey Foster, and Jo Lawson*

The goal of this project is to perform accurate, real-time American Sign Language (ASL) translation using deep learning methods. The three tasks of this project are:
- **Letter translation** (static, motionless hand signs) on individual video frames.
- **Full word translation** (dynamic hand signs) on whole video clips.
- **Realtime hand detection** from live video feed using MediaPipe. 

---
# Dataset
- **Letter translation dataset**: [asl-alphabet](https://www.kaggle.com/datasets/grassknoted/asl-alphabet)
- **Word translation dataset**: [WLASL-100](https://github.com/dxli94/WLASL) (top 100 words from whole WLASL dataset, ~5 raw videos per word)

---
# Model Architectures
- **Letter translation**: 2D CNN trained on individual video frames per letter
- **Word translation**: 
    - 3D CNN trained on whole sign videos
    - 2D CNN trained on whole sign videos superimposed into one frame
    - Transformer trained on hand keypoints extracted from whole sign videos
---
# Preprocessing
- **Letter translation**
    - Image resized to 64 x 64. 
    - Dataset size: 29,000 images (1,000 images per alphabet letter a-z, "space", "delete", and "nothing")
- **Word translation**
    - Whole videos (create_wlasl_dataset.py + preprocess_dataset.py): randomly select 2 augmentations from the augmentation set [mirror, change brightness/grayscale, speedup/slowdown, zoom in/out] per video. Resize video to (64 frames, 112 W, 112 H)
    - Superimposed frames from whole videos (before training): loop through each video and combine their np.max to one frame
    - Dataset size: 2915 total videos (3-10 raw videos per word duplicated 5 times via augmentations)
---
# Model Notebooks
- **Letter translation**
    - **CS4200_ASL_Alphabet_Demo.ipynb**: 2D CNN performing realtime translation with Mediapipe hand detection from live video feed. Achieves ~90% realtime classification accuracy
- **Word translation**
    - CS4200_stackedhands_CNN.ipynb: 2D CNN trained on stacked superimposed images created from the whole video dataset. Performed poorly, ~24% validation accuracy
    - CS4200_3DCNN.ipynb: 3D CNN trained on augmented whole video dataset. Performed pooly, ~24% validation accuracy
    - **CS4200_3DCNN_croppedhands.ipynb**: 3D CNN trained on augmented whole video dataset, with the addition of using MediaPipe to crop each signing video into two separate videos that only capture the right/left hands from each signing video. Performed slightly better than the base 3D CNN with around ~35-40% validation accuracy
    - CS4200_Transformer.ipynb: transformer trained with hand keypoints extracted from whole video dataset. Performed terribly, ~15% validation accuracy 
---
# Results
We achieved **~90% realtime accuracy when performing letter classification**. This is due to the large availability of ASL letter sign datasets. Additionally, letter-level translation is much less computationally demanding to train than word-level translation because letter signs are static, and can be represented by single frame images. On the other hand, whole words are typically dynamic signs with movement that spans multiple video frames. 

Unfortunately, we performed much poorer on whole video classification. Our main obstacle was our lack of training data: for each word in our dataset, WLASL only provided around 3-10 raw videos of that sign being performed, and these signs were typically performed by the same people. Even heavily augmenting these videos within reason could get us to around 50 unique videos per sign. To work around these limitations, we employed several approaches, such as stacking our whole videos into singular frames to train a 2D CNN, extracting keypoints from hands during signing to train a transformer, and cropping videos to include only right/left hands. However, despite our compute and dataset limitations, **we achieved 40% validation accuracy with our 3D CNN that is trained with videos cropped to include only right/left hands**, which is reasonably comparable to the SOTA results of ~60% validation accuracy from WLASL.
