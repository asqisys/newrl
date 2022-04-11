

def voting_scheme_one(self,cur,callparams):
    data=cur.execute(f'''select yes_votes as yes_votes,no_votes as no_votes,abstain_votes as abstain_votes,max_votes as max_votes from proposal where proposal_id=?''', callparams['proposal_id'])

    pass
def voting_scheme_two(self,cur,callparams):

    pass
def voting_scheme_three(self,cur,callparams):
    pass