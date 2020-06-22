# PACMAN: Capture the flag

The practical work consists of developing intelligent agents for a variation competitive game Pac-Man. In this game, I control two agents in a maze with two territories. The two agents must collaborate to defend their territory and attack opponents' territory, taking as many pacdots as possible from the enemy.

## BackGround

PacMonu is a popular video game and serves as a platform for creating Al agents that control the behaviour of PacMan and PacMan's enemies, the Ghosts. Capture the Rae (CTF) is a popular game style where two teams compete to capture a flag on the opposing side and bring it back to their side to score a point. At the end of the game, the side with the highest score wins.  
As a combination we have PacMan CTF, where each side has 2 bets that are required to coiled food pellets and bring it back to their side to score points.

## Objective

The objective is to accelerate the AI learning and practical application to building game playing agent.
I made two agents `myTeam_prev.py` is my previous agent which uses minimax algorithm with alpha-beta pruning.  
The newer version `myTeam_new.py` is using MonteCarlo simulation algorithm.

## Usages

Clone the repo and run the following command

```
python capture.py -r myTeam_new -n 10 -l RANDOM
```

This will run 10 games on random layout between my team and default baselineTeam.

## myTeam_new

### Offensive Agent

The offensive agent uses Monte Carlo simulations to evaluate each possible action at any given time. The action chosen for execution is the one that was most well evaluated.

Normally, during a simulation, the game is played randomly by all agents until it ends, and the result will be, for example, the number total victories obtained after the execution of several simulations. In this Pac-Man competition, however, this approach is not viable: the number of actions taken until the end of the game it can be very high and we don't have constant visibility of our opponent to simulate the actions. The solution to the first of these problems is widely used in real-time applications, and consists of performing simulations only to a certain depth d, that is, only d actions will be simulated of each agent. After this partial simulation, it is necessary to use a function of evaluation in the last obtained state. The solution adopted for the second problem was fix the actions of all other agents as STOP. Thus, in practice, it will be necessary to simulate only the actions of a single agent (the one who is what action to take). This solution, although quite simple, shows results promising if combined with a good evaluation function.

Two important parameters used in the Monte Carlo simulation implemented the depth of the simulation to be used and the number of simulations used to assess a certain state. Generally, the higher the value of these parameters, the better the results obtained. Thus, it is important to find values for these parameters that allow good results and leave the execution time viable.

The random simulation performed by the agent needs some care so that be more efficient. It is not interesting that the agent always chooses randomly between all possible actions at each simulation step. This can lead the agent to going back and forth, or even standing still for a few moments. Obviously, most of the time, it is not interesting that the agent is stopped or going and coming back between the same two positions during a simulation. Thus, in the execution of the random simulation, the agent is forbidden to stand still (execute the STOP action) or to reverse its direction (take the action in the opposite direction to the current direction). Note that the agent can perform these actions during the game. What is forbidden is yours use during random simulations.

### Features

The evaluation function used was based on that present in BaselineAgents. It consists of the linear combination of features and weights associated with the features. At features considered are the following:

-   **Score of the state**: takes the score of the final state of the simulation. The goal
-   **Distance to the nearest pacdot:** the distance from the agent to the nearest pacdot next in the final state of the simulation. The purpose of this feature is also maximize the possible score obtained. If, during the simulations, there are two final states with the same score, the one where the agent is closest to another pacdot is best rated.
-   **Distance to the nearest enemy**: the distance from the agent to the enemy closest to the end of the simulation. This feature allows the agent to escape the enemy if you are being chased, while trying to eat more pacdots.
-   **Pacman**: this feature indicates whether the agent is a ghost or a pacman. She is used only in a very specific situation, where it can happen for the agent to return to the defense field to defend himself and not get more return to attack because the defending enemy is on the edge watching the agent (the agent finds it advantageous to stay alive in his territory). In this case, the agent starts to prioritize the fact of being a pacman, and stops defending himself in the form of ghost, prioritizing the attack.

The weights of the features are used dynamically: normally, the largest weight goes to the feature referring to the score, a lower weight is given to the distance to enemy, a negative weight is given to the distance to the nearest pacdot (the more closer, better) and a null weight is given to the Pacman feature. If the opponent is in the scared state, the weight given to the distance to the enemy is zeroed. If our agent get stuck in the defense field, the Pacman feature gains a high weight.  
Finally, one last feature was added to the offending agent: the ability to city to avoid some alleys without pacdots. Before evaluating the possible actions, it is pre-processing was performed on the action. It is expanded to a depth 5 and, if all paths expanded from that action end in an alley without pacdots, then the agent discards the action. This feature is particularly important at the end of the game, when there are few pacdots left and going into an alley can be quite bad, cornering the agent.

### Defensive Agent

The defensive agent is quite simple. It works by defining target positions and moving looking towards them, as well as the defending agent for SimpleTeam. The definition of the target, however, is a little more elaborate. The agent sets targets in order to execute high-level strategies. These strategies are: patrolling central points from the map, check the position where pacdot disappeared, chase opponents and watch pacdots. A brief explanation of each strategy follows, explaining when it is chosen:

-   Patrol central points: this is the strategy implemented by the agent fensitive most of the time. It consists of choosing a point on the edge the territories of the two teams and move to that point. We call these patrol points. The patrol points for which the agent will be able to move are found during the pre-processing time. To choose the point to be visited, we calculated some probabilities. We associate, at each patrol point, a probability that corresponds to ` where the agent chooses to go to that position. The probability is calculated based on the inverse of the distance of the closest pacdot to the position of the point patrol in question. These values are normalized so that the sum probabilities is 1. In this way, the defending agent is more likely to move to patrol points with a nearby pacdot, since the opponent will probably try to catch these pacdots first. Whenever the opponent eats a pacdot, the odds are recalculated.
-   Check position where pacdot disappeared: the agent implemented checks, each iteration of the game, if any patdot from your territory has disappeared, a since we have information on the positions of all our pacdots. Case has disappeared, the agent will move to the position of the pacdot that disappeared. Thus, it is expected that if the enemy goes through the patrol of the defending agent, it is possible to quickly identify that our territory was invaded, as well as estimating the attacker's position.
-   Pursue opponent: during the patrol and verification previously described, if the agent sees an enemy, he starts chasing him.
-   Watch pacdots: at the end of the game, when the number of pacdots to be defended is small, it is more advantageous for the defender to move between these pacdots instead of patrolling the central area of the map. That way, when we have 4 or less pacdots, the agent starts to walk randomly from one to another.
