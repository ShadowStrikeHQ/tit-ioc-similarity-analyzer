# tit-IOC-Similarity-Analyzer
A command-line tool that takes a set of IOCs (e.g., domains, IPs, hashes) as input and calculates the similarity score between them using techniques like Jaccard index or Levenshtein distance.  This helps in clustering related threats during triage by identifying IOCs that likely belong to the same campaign, even with slight variations. - Focused on Tools that help analysts quickly triage threat intelligence feeds, correlate indicators of compromise (IOCs), and assess the relevance of threat data to their environment. Focuses on IOC processing, scoring, and reporting from different intel feeds.

## Install
`git clone https://github.com/ShadowStrikeHQ/tit-ioc-similarity-analyzer`

## Usage
`./tit-ioc-similarity-analyzer [params]`

## Parameters
- `-h`: Show help message and exit
- `-i`: A list of IOCs to analyze.
- `-m`: No description provided
- `-t`: No description provided
- `-o`: No description provided
- `-v`: Enable verbose logging.

## License
Copyright (c) ShadowStrikeHQ
