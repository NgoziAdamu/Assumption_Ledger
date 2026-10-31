from common import *
d=pd.read_excel(DATA/'biomedical/input/1-s2.0-S0092867420301070-mmc1.xlsx',header=0)
cols=['idx','Proteomics_Participant_ID','Case_excluded','Proteomics_Tumor_Normal','Age','Log2_variant_per_Mbp']
s=d.loc[d.Histologic_type.eq('Serous'),cols]
print('Case_excluded original value counts:');print(d.Case_excluded.value_counts(dropna=False).to_string())
print('All Serous rows (source dataframe row index shown):');print(s.to_string(index=True))
kept=s.loc[~s.Case_excluded.eq('Yes')]
age=kept.Age.mean();mutation=(2.0**kept.Log2_variant_per_Mbp).median()
RESULT=finish({'Serous_rows':len(s),'excluded_idxs':s.loc[s.Case_excluded.eq('Yes'),'idx'].tolist(),
 'remaining_rows':len(kept),'remaining_Age_nonmissing':int(kept.Age.notna().sum()),'remaining_log2_nonmissing':int(kept.Log2_variant_per_Mbp.notna().sum()),
 'Age_mean':float(age),'Age_mean_4dp':f'{age:.4f}','median_2_power_Log2_variant_per_Mbp':float(mutation),'median_4dp':f'{mutation:.4f}'})
