import torch
import torch.nn as nn
from torch_geometric.nn import radius_graph

from matdeeplearn.preprocessor.helpers import compute_neighbors


class BaseModel(nn.Module):
    def __init__(self, num_atoms=None, bond_feat_dim=None, num_targets=None):
        super(BaseModel, self).__init__()
        self.num_atoms = num_atoms
        self.bond_feat_dim = bond_feat_dim
        self.num_targets = num_targets

    def forward(self, data):
        raise NotImplementedError

    def generate_graph(
        self,
        data,
        cutoff=None,
        max_neighbors=None,
        use_pbc=None,
        otf_graph=None,
        mp_attr: list[str] = None,
    ):
        cutoff = cutoff or self.cutoff
        max_neighbors = max_neighbors or self.max_neighbors
        use_pbc = use_pbc or self.use_pbc
        otf_graph = otf_graph or self.otf_graph

        if not otf_graph:
            pass
            # try:
            #     if use_pbc:
            #         cell_offsets = data.cell_offsets
            #         neighbors = data.neighbors

            # except AttributeError:
            #     logging.warning(
            #         "Turning otf_graph=True as required attributes not present in data object"
            #     )
            #     otf_graph = True

        if not use_pbc:
            raise NotImplementedError("Only PBC is supported for now.")

        if use_pbc:
            edge_index = torch.cat(
                [getattr(data, f"edge_index_{attr}") for attr in mp_attr], dim=1
            )
            neighbors = getattr(data, "neighbors", None)
            edge_dist = torch.cat(
                [getattr(data, f"edge_weights_{attr}") for attr in mp_attr], dim=0
            )
            distance_vec = torch.cat(
                [getattr(data, f"edge_vec_{attr}") for attr in mp_attr], dim=0
            )
            cell_offsets = torch.cat(
                [getattr(data, f"cell_offsets_{attr}") for attr in mp_attr], dim=0
            )
            cell_offset_distances = torch.cat(
                [getattr(data, f"cell_offset_distances_{attr}") for attr in mp_attr],
            )
            neighbors = compute_neighbors(data, edge_index)

            # NOTE: we comment out the below to depend on processed data for VN functionality

            # if otf_graph:
            #     edge_index, cell_offsets, neighbors = radius_graph_pbc(
            #         cutoff, max_neighbors, data.pos, data.cell, data.n_atoms
            #     )

            # out = get_pbc_distances(
            #     data.pos,
            #     edge_index,
            #     data.cell,
            #     cell_offsets,
            #     neighbors,
            #     return_offsets=True,
            #     return_distance_vec=True,
            # )

            # edge_index = out["edge_index"]
            # edge_dist = out["distances"]
            # cell_offset_distances = out["offsets"]
            # distance_vec = out["distance_vec"]
        else:
            if otf_graph:
                edge_index = radius_graph(
                    data.pos,
                    r=cutoff,
                    batch=data.batch,
                    max_num_neighbors=max_neighbors,
                )

            j, i = edge_index
            distance_vec = data.pos[j] - data.pos[i]

            edge_dist = distance_vec.norm(dim=-1)
            cell_offsets = torch.zeros(edge_index.shape[1], 3, device=data.pos.device)
            cell_offset_distances = torch.zeros_like(
                cell_offsets, device=data.pos.device
            )
            neighbors = compute_neighbors(data, edge_index)

        return (
            edge_index,
            edge_dist,
            distance_vec,
            cell_offsets,
            cell_offset_distances,
            neighbors,
        )

    @property
    def num_params(self):
        return sum(p.numel() for p in self.parameters())

    @property
    def target_attr(self):
        return "y"