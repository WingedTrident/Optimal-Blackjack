import random
import pandas as pd

CARD_TYPES = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]


hard_hand_df = pd.read_excel("Blackjack_Totals.xlsx", sheet_name="Hard_Hand_Total", skiprows=1, index_col=1)
soft_hand_df = pd.read_excel("Blackjack_Totals.xlsx", sheet_name="Soft_Hand_Total", skiprows=1, index_col=1)
double_choice_df = pd.read_excel("Blackjack_Totals.xlsx", sheet_name="Double_Choice", skiprows=1, index_col=1)

TRIALS = 10000



def draw_card(ace_in_hand=False):
    drawn_card = random.choices(CARD_TYPES)[0]
    if drawn_card == 'A':
        if ace_in_hand:
            return 1
        return 11
    if drawn_card == 'J' or drawn_card == 'Q' or drawn_card == 'K':
        return 10
    else:
        return int(drawn_card)
    
def player_optimal_choice(player_hand, dealer_upcard):
    hand_value = sum(player_hand)
    #print(hand_value, dealer_upcard,player_hand)
    if 11 in player_hand:
        if hand_value > 31:
            return 'B'
        if hand_value > 21:
            hand_value -= 10
        optimal_choice = soft_hand_df.loc[hand_value, dealer_upcard]
        return optimal_choice
    else:
        if hand_value > 21:
            return 'B'
        optimal_choice = hard_hand_df.loc[hand_value, dealer_upcard]
        return optimal_choice

def build_hand(player_hand, dealer_face_card):
    optimal_choice = player_optimal_choice(player_hand, dealer_face_card)
    
    if optimal_choice == 'D':
        player_hand.append(draw_card(11 in player_hand))
    else:
        while (optimal_choice != 'S' and optimal_choice != 'B'):
            player_hand.append(draw_card(11 in player_hand))
            optimal_choice = player_optimal_choice(player_hand, dealer_face_card)
            #print(optimal_choice)
            
    return player_hand

            

def full_sequence():
    ## -- SET UP --
    # Dealer draws face card
    dealer_face_card = draw_card()
    
    # Player draws first card
    player_first_card = draw_card()
    
    # Dealer draws face down card
    dealer_down_card = draw_card()
    
    # Player draws second card
    player_second_card = draw_card()
    
    ## -- PLAYER DECISION -- 
    full_hand = []
    player_hand = [player_first_card, player_second_card]
    
    #SPLIT ROUTE
    if player_first_card == player_second_card and 'Y' in double_choice_df.loc[player_first_card, dealer_face_card]:
        #print("This is a split")
        double_choice = double_choice_df.loc[player_first_card, dealer_face_card]
        if player_first_card == 11: # split aces rule
            player_hand_one = [player_first_card, draw_card()]
            player_hand_two = [player_second_card, draw_card()]
        elif double_choice == 'Y' or double_choice == 'YD':
            player_hand_one = build_hand([player_first_card, draw_card()], dealer_face_card)
            player_hand_two = build_hand([player_second_card, draw_card()], dealer_face_card)
            
        full_hand.extend([player_hand_one, player_hand_two])
    # REGULAR ROUTE
    else:
        full_hand.append(build_hand(player_hand, dealer_face_card))
        
        
        
    ## -- DEALER DECISION --
    dealer_hand = [dealer_down_card, dealer_face_card]
    while ((11 in dealer_hand and sum(dealer_hand)-10 < 17 and sum(dealer_hand) > 21) or sum(dealer_hand) < 17):
        dealer_hand.append(draw_card(11 in dealer_hand))
        
    
    
    #print("DEALER CARDS: FACE: ", dealer_face_card, " DOWN: ", dealer_down_card, dealer_hand)
    #print("PLAYER CARDS: ", full_hand)
    ## -- FINAL VERDICT --
    player_wins = 0
    draws = 0
    
    for hand in full_hand:
        if (dealer_face_card+dealer_down_card) == 21 and (player_first_card+player_second_card) != 21:
            continue
        
        if sum(hand) - (10 if 11 in hand else 0) > 21:
            continue
        elif (sum(dealer_hand) - (10 if 11 in dealer_hand else 0)) > 21:
            player_wins += 1
            continue
        
        if sum(hand) == sum(dealer_hand):
            draws += 1
            continue
        
        best_player_sum = sum(player_hand)-10 if 11 in player_hand and sum(player_hand) > 21 else sum(player_hand)
        best_dealer_sum = sum(dealer_hand)-10 if 11 in dealer_hand and sum(dealer_hand) > 21 else sum(dealer_hand)
        
        if best_player_sum > best_dealer_sum:
            player_wins += 1
        
    return (player_wins, draws, len(full_hand))
    
def single_trial_calc(single_trial_logs=False):
    player_wins = 0 
    player_draws = 0
    current_trial = 0
    while current_trial < TRIALS:
        win_number, draw_number, hands_played = full_sequence()
        if single_trial_logs:
            print("Wins:", win_number, "Hands:", hands_played)
        player_wins += win_number
        player_draws += draw_number
        current_trial += hands_played
    if single_trial_logs:
        print("-------------------------------------------------------------")
        print("TOTAL WINS", player_wins, "TOTAL DRAWS", player_draws, "TOTAL LOSSES", current_trial-player_wins-player_draws, "TOTAL TRIALS", current_trial)
        print("TRIAL WIN PERCENTAGE", round(player_wins/current_trial,3)*100, "%")
        print("TRIAL DRAW PERCENTAGE", round(round(player_draws/current_trial,3)*100,2), "%")
        print("TRIAL LOSS PERCENTAGE", round((current_trial-player_wins-player_draws)/current_trial,3)*100, "%")
    return round(player_wins/current_trial,3)*100
    


def main():
    number_of_trials = 10
    percentages = []
    for _ in range(number_of_trials):
        result = single_trial_calc()
        percentages.append(round(result,3))
        
    print("Distribution:", percentages)
    print("Sorted Distribution:", sorted(percentages))
    print("Mean:", round(sum(percentages)/number_of_trials,3))
    
    
    
if __name__ == "__main__":
    main()