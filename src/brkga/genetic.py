from deap import tools, base, creator
from math import floor
import multiprocessing
from time import time


from src.individual import *
from src.brkga.population import *
from src.transfer import *


def genetic(src_struct, target, source, pos_target, 
            neg_target, facts_target, kb_source, kb_target,
            target_pred, NUM_GEN=600, pop_size=10, 
            crossover=0.6, mutation=0.3, trees=10, num_elite=0.1, num_mutation=0.1,
            num_processes = multiprocessing.cpu_count()):

    start_time = time()
    num_pop_elite = floor(num_elite*pop_size)
    num_pop_mutation = floor(num_mutation*pop_size)
    num_pop_crossover = pop_size - num_pop_elite - num_pop_mutation

    pop = Population(num_processes, pop_size)
    best_evaluates = []
    all_best_results = []

    has_same_best_value = 0
    pop.construct_population(src_struct, target, source, kb_source,
                            kb_target, target_pred)
    
    pop.evaluation(pop.population, trees, pos_target, 
                   neg_target, facts_target)


    for generation in range(NUM_GEN):
        print("GENERATION: ", generation)

        for ind in pop.population:
            ind.source_tree = ind.individual_trees
            ind.predicate_inst.kb_source = ind.predicate_inst.kb_target
            ind.predicate_inst.generate_new_preds()
            if len(ind.results) < NUM_GEN:
                ind.results.append(ind.results[-1])
            ind.predicate_inst.mapping_type = {}
      
        if len(best_evaluates) > 0 and pop.best_result() == best_evaluates[-1]:
            has_same_best_value += 1
        else:
            has_same_best_value = 0
        best_evaluates.append(pop.best_result())
#         print('MELHOR RESULTADO: ', pop.best_result())

        elite = pop.toolbox.selBest(pop.population, num_pop_elite)
        elite = pop.get_elite(pop.population, elite, num_pop_elite)

        if has_same_best_value == ((NUM_GEN)/2)+1:
            final_time = time() - start_time
            return pop, best_evaluates, all_best_results, final_time
       
        pop_next = [individual for individual in pop.population if individual not in elite]

        #crossover
        pop_next = pop.crossover(pop_next, elite, num_pop_crossover, crossover)
    
        #mutating the population
        pop_next.extend(pop.mutation(num_pop_mutation, mutation, 
                                     src_struct, target, 
                                     source, kb_source,
                                     kb_target, target_pred))

        pop_next.extend(elite)

        # evaluating new population
        pop.evaluation(pop_next, trees, pos_target, 
                       neg_target, facts_target)


        pop.population[:] = pop_next
        # all_best_results.append(pop.get_all_best_results())

        best_individuals = pop.toolbox.selBest(pop.population, 1)
        best_individuals = pop.sel_best_cll(best_individuals[0])
        for i in best_individuals:
                print(f"BEST: {i.results[-1]}")
                all_best_results.append(i.results[-1])

        # pop.print_pop()
    best_evaluates.append(pop.best_result())
    best_individuals = pop.toolbox.selBest(pop.population, 1)
    best_individuals = pop.sel_best_cll(best_individuals[0])
    for i in best_individuals:
            print(f"BEST: {i.results[-1]}")
            all_best_results.append(i.results[-1])
    
    final_time = time() - start_time
    
    return pop, best_evaluates, all_best_results, final_time
