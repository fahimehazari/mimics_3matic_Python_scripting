# 3D-Modeling-mimics-3matic
Using Python scripts for creating volume mesh of implanted cemented human femoral bones and then assigning linear/non-linear gray scale-based material properties.
## Required packages
You need to set up Python scripting for materialise software packages (mimics & 3-matic) to automate your workflow. In the following [youtube video] (https://www.youtube.com/watch?v=iVBCNZykcrc&t=10s) Python installation and how to configure mimics and 3-matic to start scripting have been demonstrated.
* mimics  
* trimatic
* numpy
* json
* globe
* math
## Creating a smooth and wrapped model in mimics
1. Generate the 3D model based on medical images using masks in mimics.
2. Run the script "wrap_and_smooth_fem.py"
3. Run the script "remove_cortex_from_cement" in case you have cemented model.
## Creating volume meshes in 3-matic
1. Import 3D models from mimics to 3-matic.
2. Run the script "non_manifold_assembly1.py", "non_manifold_assembly2.py", and "non_manifold_assembly3.py".
Note: if you perform non-manifold assembly and splitting the parts in 3-matic without scripting, for creating the mesh you can use only this script "create_mesh.py".  
## Material assignment in mimics
1. To apply linear material properties run the script "material_assignment.py".
2. To apply non-linear material properties run the script "add_non_inear-material_props.py".

## Citing

The following publication cover the technical parts of this project:
```bibtex
  authors    = {Fahimeh Azari, Amelie Sas, Karl P Kutzner, Andreas Klockow, Thierry Scheerlinck, G Harry van Lenthe},
  title     = {Cemented short‐stem total hip arthroplasty: Characteristics of line‐to‐line versus undersized cementing techniques using a validated CT‐based finite element analysis},
  booktitle = {Journal of Orthopaedic Research®},
  Issue = {8},
  Volume = {39},
  pages = {1681--1690},
  url = {https://onlinelibrary.wiley.com/doi/abs/10.1002/jor.24887},
  publisher = {Wiley},
  year      = {2021},
  month     = {August}
}
```
