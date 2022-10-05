class Summary():
    def __init__(self, df):
        self.df = df
        self.df_summary = {'diff' : dict(), 'pct_change' : dict()}
        for a, b in [('like', 'media'), ('comments', 'media')]:
            self._calc_ab_ratio(a, b)

    def get_summaries(self, summary_func:iter = ['diff'], periods:iter = [1], fillna = False):
        df_summaries = self.df.copy()
        for s in summary_func:
            for p in periods:
                self._summarize(summary_func = s, periods = p)
                df_summaries = df_summaries.join(self.df_summary[s][p])
        return df_summaries    

    def _summarize(self, summary_func = 'diff', periods=1, fillna = False):
        if periods in self.df_summary[summary_func].keys():
            return    
        if summary_func == 'diff':
            defined_func = lambda x: x.diff(periods)
        elif summary_func == 'pct_change':
            defined_func = lambda x: x.pct_change(periods) * 100
        df_summary = self.df.groupby('name')[[c for c in self.df.columns if ('count' in c) or ('ratio' in c)]].transform(defined_func)
        df_summary.columns = [c.split('_count')[0] + f'_{summary_func}' for c in df_summary.columns]
        if fillna:
            df_summary = df_summary.fillna(0)
        self.df_summary[summary_func][periods] = df_summary

    def _calc_ab_ratio(self, a, b):
        self.df[f'{a}_{b}_ratio'] = self.df[f'{a}_count'] / self.df[f'{b}_count']
