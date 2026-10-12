"""
RGCN Model Architecture for MGTAB Bot Detection
=================================================

Implements a Relational Graph Convolutional Network (RGCN)
for binary node classification (Human vs Bot) on the MGTAB
multi-relational Twitter graph.

Architecture:
    Input (788 features)
        -> RGCNConv (788 -> hidden_dim, 7 relations, basis decomposition)
        -> BatchNorm -> ReLU -> Dropout
        -> RGCNConv (hidden_dim -> hidden_dim, 7 relations, basis decomposition)
        -> BatchNorm -> ReLU -> Dropout
        -> Linear (hidden_dim -> 2 classes)

Reference:
    Schlichtkrull et al., "Modeling Relational Data with Graph
    Convolutional Networks", ESWC 2018.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import RGCNConv


class RGCNBotDetector(nn.Module):
    """
    2-layer RGCN for binary bot detection on multi-relational graphs.

    Parameters
    ----------
    in_channels : int
        Number of input node features (788 for MGTAB: 20 profile + 768 embeddings).
    hidden_channels : int
        Hidden representation dimension.
    out_channels : int
        Number of output classes (2 for Human/Bot).
    num_relations : int
        Number of edge/relation types (7 for MGTAB).
    num_bases : int or None
        Number of bases for basis decomposition in RGCNConv.
        Reduces parameters from O(num_relations * in * out) to
        O(num_bases * in * out + num_relations * num_bases).
        Set to None to disable decomposition.
    dropout : float
        Dropout probability applied after each hidden layer.
    """

    def __init__(
        self,
        in_channels: int = 788,
        hidden_channels: int = 64,
        out_channels: int = 2,
        num_relations: int = 7,
        num_bases: int = 4,
        dropout: float = 0.3,
    ):
        super().__init__()

        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.out_channels = out_channels
        self.num_relations = num_relations
        self.num_bases = num_bases
        self.dropout = dropout

        # Layer 1: Input -> Hidden
        self.conv1 = RGCNConv(
            in_channels=in_channels,
            out_channels=hidden_channels,
            num_relations=num_relations,
            num_bases=num_bases,
        )
        self.bn1 = nn.BatchNorm1d(hidden_channels)

        # Layer 2: Hidden -> Hidden
        self.conv2 = RGCNConv(
            in_channels=hidden_channels,
            out_channels=hidden_channels,
            num_relations=num_relations,
            num_bases=num_bases,
        )
        self.bn2 = nn.BatchNorm1d(hidden_channels)

        # Classification head
        self.classifier = nn.Linear(hidden_channels, out_channels)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
    ) -> torch.Tensor:
        """
        Forward pass.

        Parameters
        ----------
        x : Tensor [num_nodes, in_channels]
            Node feature matrix.
        edge_index : Tensor [2, num_edges]
            Edge connectivity in COO format.
        edge_type : Tensor [num_edges]
            Relation type for each edge.

        Returns
        -------
        Tensor [num_nodes, out_channels]
            Raw logits (unnormalized) for each class.
        """
        # Layer 1
        h = self.conv1(x, edge_index, edge_type)
        h = self.bn1(h)
        h = F.relu(h)
        h = F.dropout(h, p=self.dropout, training=self.training)

        # Layer 2
        h = self.conv2(h, edge_index, edge_type)
        h = self.bn2(h)
        h = F.relu(h)
        h = F.dropout(h, p=self.dropout, training=self.training)

        # Classification
        out = self.classifier(h)
        return out

    def get_embeddings(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
    ) -> torch.Tensor:
        """
        Returns the learned node embeddings (before classification head).
        Useful for downstream analysis or visualization.
        """
        h = self.conv1(x, edge_index, edge_type)
        h = self.bn1(h)
        h = F.relu(h)

        h = self.conv2(h, edge_index, edge_type)
        h = self.bn2(h)
        h = F.relu(h)

        return h

    def count_parameters(self) -> int:
        """Returns total number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def __repr__(self) -> str:
        return (
            f"RGCNBotDetector(\n"
            f"  in_channels={self.in_channels},\n"
            f"  hidden_channels={self.hidden_channels},\n"
            f"  out_channels={self.out_channels},\n"
            f"  num_relations={self.num_relations},\n"
            f"  num_bases={self.num_bases},\n"
            f"  dropout={self.dropout},\n"
            f"  trainable_params={self.count_parameters():,}\n"
            f")"
        )
