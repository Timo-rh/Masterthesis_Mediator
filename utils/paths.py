from os import path

# Main directories
utils_dir = path.dirname(path.realpath(__file__))
ips_dir = path.dirname(utils_dir)
root_dir = path.dirname(ips_dir)
results_dir = path.join(root_dir, 'results')

# Prompts
prompt_dir = path.join(ips_dir, 'prompts')
type_extraction_prompts = path.join(prompt_dir, '1_type_extraction')        #Referenziert auf den prompts/1_type_extraction ordner (von da aus kann feedback und main.txt aufgerufen werden)
type_hierarchy_prompts = path.join(prompt_dir, '2_hierarchy_construction')
action_extraction_prompts = path.join(prompt_dir, '3_action_extraction')
action_construction_prompts = path.join(prompt_dir, '4_action_construction')
state_goal_extraction_prompts = path.join(prompt_dir, '5_task_extraction')

# Domains (with underlying tasks)
blocksworld = path.join(ips_dir, 'blocksworld')
household = path.join(ips_dir, 'household')
isr = path.join(ips_dir, 'isr')
isr_assisted = path.join(ips_dir, 'isr_assisted')
logistics = path.join(ips_dir, 'logistics')
tyreworld = path.join(ips_dir, 'tyreworld')

# External tools
scorpion_dir = path.join(root_dir, 'scorpion')

# parser
ohne_feedback_dir = path.join(results_dir, 'ohne_feedback')