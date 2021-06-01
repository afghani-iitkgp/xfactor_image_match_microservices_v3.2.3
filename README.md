**FaceNet Model**

FaceNet is a face recognition system that was described by Florian Schroff, et al. at Google in their 2015 paper titled “FaceNet: A Unified Embedding for Face Recognition and Clustering.”

It is a system that, given a picture of a face, will extract high-quality features from the face and predict a 128 element vector representation these features, called a face embedding.

_FaceNet, that directly learns a mapping from face images to a compact Euclidean space where distances directly correspond to a measure of face similarity._

1. The model is a deep convolutional neural network trained via a triplet loss function that encourages vectors for the same identity to become more similar (smaller distance), 
whereas vectors for different identities are expected to become less similar (larger distance). 

    _The focus on training a model to create embeddings directly (rather than extracting them from an intermediate layer of a model) was an important innovation in this work._

2. These face embeddings were then used as the basis for training classifier systems on standard face recognition benchmark datasets, achieving then-state-of-the-art results.
=======
# xfactor_image_match_microservices_v2

First, you create your branch locally:

git checkout -b <branch-name> # Create a new branch and check it out
The remote branch is automatically created when you push it to the remote server. So when you feel ready for it, you can do:

git push <remote-name> <branch-name> 
Where <remote-name> is typically origin, the name which git gives to the remote you cloned from. Your colleagues would then just pull that branch, and it's automatically created locally.

Note however that formally, the format is:

git push <remote-name> <local-branch-name>:<remote-branch-name>
But when you omit one, it assumes both branch names are the same. Having said this, as a word of caution, do not make the critical mistake of specifying only :<remote-branch-name> (with the colon), or the remote branch will be deleted!

So that a subsequent git pull will know what to do, you might instead want to use:

git push --set-upstream <remote-name> <local-branch-name> 
As described below, the --set-upstream option sets up an upstream branch:

For every branch that is up to date or successfully pushed, add upstream (tracking) reference, used by argument-less git-pull(1) and other commands.
