import pandas as pd, numpy as np
out=[]
for model in ['human2','recon3d']:
    d=pd.read_csv(f'results/scans/class_{model}_full.csv')
    d=d[d['type']=='II']
    for r in d.itertuples():
        out.append(dict(model=model,reaction=r.reaction_id,endpoint=r.metric,
                        u_star=round(float(r.u_opt),2),J0=round(float(r.J0),3),
                        Jstar=round(float(r.J_opt),3),J1=round(float(r.J1),3)))
t1=pd.DataFrame(out); t1.to_csv('manuscript/table1_typeII_hits.csv',index=False)
r=pd.read_csv('results/robustness_matrix.csv')
r[['cond','sel','mod']]=r['config'].str.extract(r'(aerobic|glucose_limited|oxygen_limited)_(pfba|moma_linear)_(fva_informed|bound_scaling)',expand=True)
t4=r.pivot_table(index=['model','cond','sel','mod'],values='n_interior',aggfunc='first').reset_index()
t4.to_csv('manuscript/table4_robustness.csv',index=False)
print(f'table1 {len(t1)} rows; table4 {len(t4)} rows')
