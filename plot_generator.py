import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import os

class PlotGenerator:
    def __init__(self, df, plots_dir):
        self.df = df
        self.plots_dir = plots_dir
    
    def generate_all_plots(self):
        plot_files = []
        
        plot_files.append(self.generate_binding_distribution())
        
        plot_files.append(self.generate_density_plot())
        
        plot_files.append(self.generate_box_plot())
        
        plot_files.append(self.generate_rmsd_distribution())
        
        plot_files.append(self.generate_3d_scatter())
        
        plot_files.append(self.generate_affinity_vs_rmsd_ub())
        
        plot_files.append(self.generate_affinity_vs_rmsd_lb())
        
        plot_files.append(self.generate_pairwise_plot())
        
        return [p for p in plot_files if p is not None]
    
    def generate_binding_distribution(self):
        if 'binding_affinity' not in self.df.columns:
            return None
        
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['binding_affinity'], bins=30, edgecolor='black', alpha=0.7, color='skyblue')
        plt.xlabel('Binding Affinity (kcal/mol)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Binding Affinity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_path = os.path.join(self.plots_dir, '1_binding_affinity_distribution.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return ('1_binding_affinity_distribution.png', 'Distribution of Binding Affinity')
    
    def generate_density_plot(self):
        if 'binding_affinity' not in self.df.columns:
            return None
        
        fig = plt.figure(figsize=(10, 6))
        sns.kdeplot(data=self.df['binding_affinity'], fill=True, color='green', alpha=0.5)
        plt.xlabel('Binding Affinity (kcal/mol)')
        plt.ylabel('Density')
        plt.title('Density Plot of Binding Affinity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_path = os.path.join(self.plots_dir, '2_density_plot_binding_affinity.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return ('2_density_plot_binding_affinity.png', 'Density Plot of Binding Affinity')
    
    def generate_box_plot(self):
        if 'binding_affinity' not in self.df.columns:
            return None
        
        fig = plt.figure(figsize=(8, 6))
        plt.boxplot(self.df['binding_affinity'].dropna(), patch_artist=True, 
                   boxprops=dict(facecolor='lightblue'))
        plt.ylabel('Binding Affinity (kcal/mol)')
        plt.title('Box Plot of Binding Affinity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_path = os.path.join(self.plots_dir, '3_box_plot_binding_affinity.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return ('3_box_plot_binding_affinity.png', 'Box Plot of Binding Affinity')
    
    def generate_rmsd_distribution(self):
        if not all(col in self.df.columns for col in ['rmsd_ub', 'rmsd_lb']):
            return None
        
        fig = plt.figure(figsize=(10, 6))
        plt.hist(self.df['rmsd_ub'].dropna(), bins=30, alpha=0.7, label='RMSD ub', color='blue')
        plt.hist(self.df['rmsd_lb'].dropna(), bins=30, alpha=0.7, label='RMSD lb', color='red')
        plt.xlabel('RMSD (Å)')
        plt.ylabel('Frequency')
        plt.title('Distribution of RMSD')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_path = os.path.join(self.plots_dir, '4_distribution_rmsd.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return ('4_distribution_rmsd.png', 'Distribution of RMSD')
    
    def generate_3d_scatter(self):
        if not all(col in self.df.columns for col in ['binding_affinity', 'rmsd_ub', 'rmsd_lb']):
            return None
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        sc = ax.scatter(self.df['rmsd_ub'], self.df['rmsd_lb'], 
                      self.df['binding_affinity'],
                      c=self.df['binding_affinity'], cmap='viridis',
                      s=50, alpha=0.7)
        
        ax.set_xlabel('RMSD ub (Å)')
        ax.set_ylabel('RMSD lb (Å)')
        ax.set_zlabel('Binding Affinity (kcal/mol)')
        ax.set_title('3D Scatter: Binding Affinity vs RMSD')
        
        plt.colorbar(sc, ax=ax, label='Binding Affinity', shrink=0.5)
        plt.tight_layout()
        
        plot_path = os.path.join(self.plots_dir, '5_3d_scatter_affinity_vs_rmsd.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return ('5_3d_scatter_affinity_vs_rmsd.png', '3D Scatter Plot')
    
    def generate_affinity_vs_rmsd_ub(self):
        if 'rmsd_ub' not in self.df.columns or 'binding_affinity' not in self.df.columns:
            return None
        
        fig = plt.figure(figsize=(10, 6))
        plt.scatter(self.df['rmsd_ub'], self.df['binding_affinity'], 
                   alpha=0.6, s=50, c=self.df['binding_affinity'], cmap='coolwarm')
        plt.xlabel('RMSD ub (Å)')
        plt.ylabel('Binding Affinity (kcal/mol)')
        plt.title('Binding Affinity vs RMSD ub')
        plt.colorbar(label='Binding Affinity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_path = os.path.join(self.plots_dir, '6_affinity_vs_rmsd_ub.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return ('6_affinity_vs_rmsd_ub.png', 'Binding Affinity vs RMSD ub')
    
    def generate_affinity_vs_rmsd_lb(self):
        if 'rmsd_lb' not in self.df.columns or 'binding_affinity' not in self.df.columns:
            return None
        
        fig = plt.figure(figsize=(10, 6))
        plt.scatter(self.df['rmsd_lb'], self.df['binding_affinity'], 
                   alpha=0.6, s=50, c=self.df['binding_affinity'], cmap='plasma')
        plt.xlabel('RMSD lb (Å)')
        plt.ylabel('Binding Affinity (kcal/mol)')
        plt.title('Binding Affinity vs RMSD lb')
        plt.colorbar(label='Binding Affinity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_path = os.path.join(self.plots_dir, '7_affinity_vs_rmsd_lb.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        return ('7_affinity_vs_rmsd_lb.png', 'Binding Affinity vs RMSD lb')
    
    def generate_pairwise_plot(self):
        if not all(col in self.df.columns for col in ['binding_affinity', 'rmsd_ub', 'rmsd_lb']):
            return None
        
        try:
            plot_data = self.df[['binding_affinity', 'rmsd_ub', 'rmsd_lb']].dropna()
            
            fig, axes = plt.subplots(3, 3, figsize=(12, 12))
            fig.suptitle('Pairwise Relationships', fontsize=16, y=1.02)
            
            variables = ['binding_affinity', 'rmsd_ub', 'rmsd_lb']
            names = ['Binding Affinity', 'RMSD ub', 'RMSD lb']
            
            for i in range(3):
                for j in range(3):
                    ax = axes[i, j]
                    
                    if i == j:
                        ax.hist(plot_data[variables[i]], bins=20, alpha=0.7, edgecolor='black')
                        ax.set_xlabel(names[i])
                        ax.set_ylabel('Frequency')
                        if i == 0:
                            ax.set_title('Distribution')
                    else:
                        ax.scatter(plot_data[variables[j]], plot_data[variables[i]], 
                                 alpha=0.6, s=20)
                        ax.set_xlabel(names[j])
                        ax.set_ylabel(names[i])
                    
                    ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            plot_path = os.path.join(self.plots_dir, '8_pairwise_relationships.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            return ('8_pairwise_relationships.png', 'Pairwise Relationships')
        except:
            return None