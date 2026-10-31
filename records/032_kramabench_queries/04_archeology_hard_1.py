from common import *
d=pd.read_excel(DATA/'archeology/input/climateMeasurements.xlsx',header=5)
c=d[['Age_ky','K']].dropna().sort_values('Age_ky')
# Integer years avoid endpoint drift from repeated floating-point addition.
ages=np.arange(6005,6413,dtype=np.int64)/1000.0
values=np.interp(ages,c.Age_ky,c.K)
print('valid source rows',len(c),'duplicate age rows',int(c.Age_ky.duplicated().sum()))
print(pd.DataFrame({'Age_ky':ages,'interpolated_K':values}).to_string(index=False))
value=float(values.mean());target=8577.5298
RESULT=finish({'valid_source_rows':len(c),'sample_count':len(ages),'start_ky':float(ages[0]),'end_ky':float(ages[-1]),
 'mean_K':value,'rounded_4':round(value,4),'comparison':target,'difference_computed_minus_comparison':value-target,'rounded_4_difference':round(value,4)-target})
