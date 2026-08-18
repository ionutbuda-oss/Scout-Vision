from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from .card_data import build_card_context,safe_filename
from .renderer import render_html,render_png
DEFAULT_RANKINGS=Path('outputs/rankings/France_L3_U25_rankings.xlsx');DEFAULT_OUTPUT=Path('outputs/player_cards')

def create_top_player_cards(rankings_file:Path,output_folder:Path,competition_name:str,top_n_per_position:int=5)->list[Path]:
    rankings_file=Path(rankings_file);output_folder=Path(output_folder)
    df=pd.read_excel(rankings_file,sheet_name='All Ranked')
    for c in ['Recruitment Score','Performance Score']:df[c]=pd.to_numeric(df[c],errors='coerce')
    template=Path(__file__).resolve().parent/'templates'/'player_card.html'; htmlroot=output_folder.parent/'card_html'; made=[]
    for group in df['Position Group'].dropna().astype(str).drop_duplicates():
        players=df[df['Position Group'].astype(str)==group].sort_values(['Recruitment Score','Performance Score'],ascending=False)
        for _,row in players.head(top_n_per_position).iterrows():
            gs=safe_filename(group);ps=safe_filename(row['Player']);ctx=build_card_context(row,competition_name=competition_name)
            hp=htmlroot/gs/f'{ps}.html'; pp=output_folder/gs/f'{ps}.png';render_html(template,ctx,hp);render_png(hp,pp);made.append(pp)
    return made

def generate_single_player_card(rankings_file:Path,player_name:str,competition_name:str,output_folder:Path)->Path:
    df=pd.read_excel(rankings_file,sheet_name='All Ranked');m=df[df['Player'].astype(str).str.strip().str.casefold()==player_name.strip().casefold()]
    if m.empty:raise ValueError(f'Player not found: {player_name}')
    row=m.iloc[0];ctx=build_card_context(row,competition_name=competition_name);template=Path(__file__).resolve().parent/'templates'/'player_card.html';slug=safe_filename(row['Player']);hp=output_folder/f'{slug}.html';pp=output_folder/f'{slug}.png';render_html(template,ctx,hp);return render_png(hp,pp)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rankings',type=Path,default=DEFAULT_RANKINGS);ap.add_argument('--output',type=Path,default=DEFAULT_OUTPUT);ap.add_argument('--competition',default='France - Ligue 3');ap.add_argument('--top',type=int,default=5);ap.add_argument('--player')
    a=ap.parse_args()
    if a.player:print(generate_single_player_card(a.rankings,a.player,a.competition,a.output.parent/'concept_b_test').resolve())
    else:print(f'Created {len(create_top_player_cards(a.rankings,a.output,a.competition,a.top))} cards in {a.output.resolve()}')
if __name__=='__main__':main()
