#python remove_skopos_maintenance_contracts.py input.sfs output.sfs [1 2 3]
#input.sfs: your original save.
#output.sfs: new file.
#enter desired level to clear '1', '2', '3' 

import argparse
import re

def parse_sfs_block(lines, start_index):
    """
    Parse a single block starting from lines[start_index].
    Returns the end index of the block and the block lines.
    """
    block = [lines[start_index]]  # Add identifier line
    i = start_index + 1
    if i >= len(lines) or lines[i].strip() != '{':
        # Not a proper block, treat as single line
        return i, block
    block.append(lines[i])
    depth = 1
    i += 1
    while i < len(lines) and depth > 0:
        line = lines[i]
        block.append(line)
        depth += line.count('{') - line.count('}')
        i += 1
    return i, block

def check_contract(block, level, logfile):
    """
    Check if the block should be removed.
    - Must have agentName = agent_name (ignoring whitespace)
    - title must contain keyword
    - title must match one of the levels criteria
    """
    agent_found=False
    for line in block:
        line = line.strip()
        if 'agentName = skopos_telecom_agent' in line:
            logfile.write(' Found skopos agent >>'+line+'\n')
            agent_found=True;
        if (agent_found and 'title =' in line):
            if f'Level {level}' in line:
                logfile.write(' Found level match >>'+level+'\n')
                return True
            else:
                logfile.write(' No level match >>'+level+'\n')
                return False
    return False

def remove_contracts(input_file, output_file, level):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    output_log = 'sfslog.txt'
    logfile = open(output_log, 'w', encoding='utf-8')
    i = 0
    output_lines = []
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r'^\s*(CONTRACT|CONTRACT_FINISHED)\s*$', line):
            logfile.write('Found contract at line '+str(i+1)+' >>'+line+'\n')
            end_i, block = parse_sfs_block(lines, i)
            if check_contract(block, level, logfile):
                # Skip this block
                logfile.write(' ########## matching contract detected at block stating at line '+str(i+1)+' and ending at line '+str(end_i+1)+'\n')
                i = end_i
                continue
            else:
                output_lines.extend(block)
                i = end_i
                continue
        else:
            output_lines.append(lines[i])
            i += 1
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    logfile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove specific contracts from KSP .sfs save file.')
    parser.add_argument('input_file', type=str, help='Path to input .sfs file')
    parser.add_argument('output_file', type=str, help='Path to output .sfs file')
    parser.add_argument('level', type=str, help='Level to remove: 1, 2 or 3')
    args = parser.parse_args()
    
    remove_contracts(args.input_file, args.output_file, args.level)
    