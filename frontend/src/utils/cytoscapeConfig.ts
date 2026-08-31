import cytoscape from 'cytoscape';
import { GraphLayoutAlgorithm } from '../types/network';

// Edge color mapping by relationship type in MGTAB
export const RELATIONSHIP_COLORS: Record<string, string> = {
  FOLLOW: '#475569',       // Slate 600
  FRIEND: '#6366F1',       // Indigo 500
  RETWEET: '#06B6D4',      // Cyan 500
  MENTION: '#A855F7',      // Purple 500
  REPLY: '#F59E0B',        // Amber 500
  CO_ENGAGEMENT: '#EC4899', // Pink 500
};

// Cytoscape stylesheet tailored for Dark Research UI
export const getCytoscapeStylesheet = (): cytoscape.StylesheetStyle[] => [
  // Base Node Style
  {
    selector: 'node',
    style: {
      'background-color': '#64748B',
      'label': 'data(label)',
      'color': '#E2E8F0',
      'font-size': 11,
      'font-weight': 'bold',
      'text-valign': 'bottom',
      'text-margin-y': 6,
      'text-background-opacity': 0.85,
      'text-background-color': '#0F172A',
      'text-background-padding': '3px',
      'text-background-shape': 'roundrectangle',
      'border-width': 2,
      'border-color': '#334155',
      'width': 'mapData(degree, 0, 300, 24, 60)' as unknown as number,
      'height': 'mapData(degree, 0, 300, 24, 60)' as unknown as number,
      'transition-property': 'background-color, border-color, width, height',
      'transition-duration': 0.25,
    },
  },

  // Bot Node Style
  {
    selector: 'node[prediction = "BOT"]',
    style: {
      'background-color': '#EF4444',
      'border-color': '#FCA5A5',
      'border-width': 2.5,
    },
  },

  // Human Node Style
  {
    selector: 'node[prediction = "HUMAN"]',
    style: {
      'background-color': '#10B981',
      'border-color': '#6EE7B7',
      'border-width': 2.5,
    },
  },

  // Seed / Active Center Node
  {
    selector: 'node[?is_seed]',
    style: {
      'border-color': '#F59E0B',
      'border-width': 4,
    },
  },

  // Selected Node Style
  {
    selector: 'node:selected',
    style: {
      'border-color': '#38BDF8',
      'border-width': 4,
    },
  },

  // Base Edge Style
  {
    selector: 'edge',
    style: {
      'width': 2,
      'line-color': '#475569',
      'target-arrow-color': '#475569',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'opacity': 0.7,
      'arrow-scale': 0.8,
    },
  },

  // Retweet Edges
  {
    selector: 'edge[relationship = "RETWEET"]',
    style: {
      'line-color': '#06B6D4',
      'target-arrow-color': '#06B6D4',
      'width': 2.5,
      'opacity': 0.85,
    },
  },

  // Mention Edges
  {
    selector: 'edge[relationship = "MENTION"]',
    style: {
      'line-color': '#A855F7',
      'target-arrow-color': '#A855F7',
      'width': 2.5,
      'opacity': 0.85,
    },
  },

  // Friend Edges
  {
    selector: 'edge[relationship = "FRIEND"]',
    style: {
      'line-color': '#6366F1',
      'target-arrow-color': '#6366F1',
      'width': 2,
    },
  },

  // Reply Edges
  {
    selector: 'edge[relationship = "REPLY"]',
    style: {
      'line-color': '#F59E0B',
      'target-arrow-color': '#F59E0B',
      'width': 2,
    },
  },

  // Selected Edge Style
  {
    selector: 'edge:selected',
    style: {
      'line-color': '#F8FAFC',
      'target-arrow-color': '#F8FAFC',
      'width': 4,
      'opacity': 1.0,
    },
  },
];

// Layout Generator Helper
export function getLayoutConfig(algorithm: GraphLayoutAlgorithm): cytoscape.LayoutOptions {
  switch (algorithm) {
    case 'concentric':
      return {
        name: 'concentric',
        concentric: (node: cytoscape.NodeSingular) => {
          return node.data('pagerank') ? node.data('pagerank') * 1000 : node.data('degree') || 10;
        },
        levelWidth: () => 1,
        padding: 50,
        animate: true,
        animationDuration: 500,
      };
    case 'circle':
      return {
        name: 'circle',
        padding: 50,
        animate: true,
        animationDuration: 500,
      };
    case 'breadthfirst':
      return {
        name: 'breadthfirst',
        directed: true,
        padding: 50,
        animate: true,
        animationDuration: 500,
      };
    case 'grid':
      return {
        name: 'grid',
        padding: 50,
        animate: true,
        animationDuration: 500,
      };
    case 'cose':
    default:
      return {
        name: 'cose',
        idealEdgeLength: () => 90,
        nodeOverlap: 20,
        refresh: 20,
        fit: true,
        padding: 40,
        randomize: false,
        componentSpacing: 100,
        nodeRepulsion: () => 450000,
        edgeElasticity: () => 100,
        nestingFactor: 5,
        gravity: 80,
        numIter: 800,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
        animate: false,
      };
  }
}
