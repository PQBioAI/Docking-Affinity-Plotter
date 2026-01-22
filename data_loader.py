import pandas as pd

class DataLoader:
    def __init__(self, csv_path):
        self.csv_path = csv_path
    
    def load_data(self):
        df = pd.read_csv(self.csv_path)
        df.columns = df.columns.str.strip()
        
        column_mapping = {
            'rmsd/ub': 'rmsd_ub',
            'rmsd/lb': 'rmsd_lb',
            'Binding Affinity': 'binding_affinity',
            'Ligand': 'ligand',
            'rmsd': 'rmsd_ub'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)
        
        df = df.drop_duplicates()
        
        numeric_cols = ['binding_affinity', 'rmsd_ub', 'rmsd_lb']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_top_ligands(self, df):
        if not all(col in df.columns for col in ['ligand', 'binding_affinity', 'rmsd_ub', 'rmsd_lb']):
            return pd.DataFrame()
        
        filtered_df = df[
            (df['rmsd_ub'] == 0) & 
            (df['rmsd_lb'] == 0)
        ].copy()
        
        if len(filtered_df) == 0:
            filtered_df = df.copy()
        
        filtered_df = filtered_df.sort_values('binding_affinity')
        top_ligands = filtered_df.head(10).copy()
        
        return top_ligands