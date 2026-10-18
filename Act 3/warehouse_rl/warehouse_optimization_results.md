# Assignment 5: Warehouse Optimization Results

## Optimization Approach

I focused on where products were stored because unnecessary walking takes time away from completing orders. Moving a popular product closer to delivery can help, but the benefit must justify the manager’s travel and moving another product farther away. My agent compares those effects before requesting a swap, checks that storage locations are accessible, and waits for an available manager. I also corrected staffing behavior so layout decisions could be carried out without excessive hiring or interrupting active workers.

## Benchmark Method

Each benchmark evaluated all eight agents over 10 episodes. The results below report my skeleton_optimization agent’s placement, average total profit per episode, and approximate 95% confidence interval margin.

## Results

In the initial 10-episode benchmark, my agent placed eighth out of eight agents, with an average profit of -$1,012.65 and a reported 95% confidence interval of ±$4.48. Its average order completion rate was 34.8%.

After implementing frequency-based layout optimization and correcting employee counting, manager detection, and hiring limits, my agent moved to second place. Average profit reached $21,520.79, with a reported 95% confidence interval of ±$5,188.11, and the completion rate increased to 58.9%.

For the second improvement, I prioritized keeping a manager available and prevented firing employees who were completing active tasks.
My agent finished first out of eight, earning an average profit of $34,879.35 with a reported 95% confidence interval of ±$3,124.66.
Its completion rate reached 68.7%. Compared with the first improved version, it earned more profit and had a narrower confidence interval, suggesting more consistent performance across the 10 episodes.

## Implementation Changes

First improvement:
- Replaced random layout swaps with greedy selection based on
  retrieval frequency, product copy counts, and delivery distance.
- Accounted for the displaced product when estimating swap benefits.
- Favored swaps requiring less manager travel.
- Restricted swaps to accessible storage cells with an idle manager.
- Corrected employee counting, manager detection, and hiring limits.

Second improvement:
- Prioritized hiring a manager when none was available.
- Prevented firing the manager or interrupting workers with active tasks.
- Added diagnostic output showing relocations started and completed.

## Interpretation

Average profit increased by $35,892.00 from baseline to the final
version. Completion rate increased by 33.9 percentage points.

The final average profit exceeded the runner-up, aggressive_swap ($20,613.17), by $14,266.18. The final reported confidence interval was approximately $31,754.69–$38,004.01.

The baseline's narrow interval reflects consistently poor results near the bankruptcy cutoff. It does not indicate effective operation.

Both layout optimization and staffing corrections contributed to the improved system. These experiments do not isolate the effect of layout alone. Randomness also affects comparisons between runs.

## Future Improvements

- Group products frequently ordered together.
- Include aisle congestion and actual walking paths in swap scoring.
- Estimate whether future retrieval savings justify relocation costs.
- Compare layout strategies with staffing held constant and matched random seeds to better isolate their effects.

## Reflection
My goal was to improve warehouse profit by making product placement decisions based on actual retrieval activity. Across the 10-episode benchmarks, my agent improved from eighth out of eight with an average profit of −$1,012.65 to first with $34,879.35, a gain of $35,892.00. Order completion increased from 34.8% to 68.7%. The first improved version reached second place at $21,520.79, but its reported 95% confidence interval of ±$5,188.11 showed considerable variability. After protecting the manager and preventing the dismissal of busy workers, average profit increased further, and the interval narrowed to ±$3,124.66. The final version also exceeded aggressive_swap, the runner-up, by $14,266.18 in average profit. These results demonstrate improvement across repeated episodes, although they do not prove that layout changes alone caused the gains because I also corrected staffing behavior. This process taught me that an effective optimization strategy depends on having the operational support needed to carry out its decisions.

I replaced random swaps with a greedy algorithm that evaluates accessible storage locations every 100 steps and selects the swap with the highest positive estimated benefit. It estimates demand per product copy from retrieval frequency and favors moving frequently retrieved products closer to delivery bays. It also accounts for the product moved farther away and favors shorter manager travel, balancing future retrieval savings against relocation effort. Swaps require an idle manager, and the agent leaves the layout unchanged when no beneficial move is found. Staffing corrections enforce the employee limit and preserve the manager and active workers, helping the layout strategy operate consistently. The scoring function estimates travel benefits rather than directly calculating profit, and Manhattan distance does not capture aisle obstacles or congestion. Future improvements would group products frequently ordered together, use actual walking distances, and estimate whether savings over the remaining simulation justify a relocation. I would also compare layout strategies with identical staffing rules and matched random seeds to measure their individual effects more clearly.