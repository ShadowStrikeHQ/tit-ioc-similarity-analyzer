import argparse
import logging
import sys
from collections import Counter
import pandas as pd
from tabulate import tabulate
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def jaccard_similarity(set1, set2):
    """
    Calculates the Jaccard similarity between two sets.

    Args:
        set1 (set): The first set.
        set2 (set): The second set.

    Returns:
        float: The Jaccard similarity score (between 0 and 1).
    """
    try:
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        if union == 0:
            return 0.0  # Handle the case where both sets are empty
        return intersection / union
    except Exception as e:
        logging.error(f"Error calculating Jaccard similarity: {e}")
        return 0.0

def levenshtein_distance(s1, s2):
    """
    Calculates the Levenshtein distance between two strings.

    Args:
        s1 (str): The first string.
        s2 (str): The second string.

    Returns:
        int: The Levenshtein distance.
    """
    try:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
    except Exception as e:
        logging.error(f"Error calculating Levenshtein distance: {e}")
        return float('inf')  # Return infinity on error

def normalize_ioc(ioc):
    """
    Normalizes an IOC by lowercasing and removing common prefixes/suffixes.

    Args:
        ioc (str): The IOC to normalize.

    Returns:
        str: The normalized IOC.
    """
    try:
        ioc = ioc.lower().strip()
        # Remove common prefixes and suffixes (e.g., http://, www., .com)
        ioc = re.sub(r"^(http://|https://|www\.)", "", ioc)
        ioc = re.sub(r"(\.com|\.net|\.org|\.io)$", "", ioc)
        return ioc
    except Exception as e:
        logging.error(f"Error normalizing IOC: {e}")
        return ioc

def calculate_similarity(iocs, similarity_metric="jaccard", threshold=0.8):
    """
    Calculates the similarity between all pairs of IOCs.

    Args:
        iocs (list): A list of IOCs.
        similarity_metric (str): The similarity metric to use ("jaccard" or "levenshtein").
        threshold (float): The similarity threshold to consider IOCs as similar.

    Returns:
        pandas.DataFrame: A DataFrame containing the similarity scores between all IOC pairs.
    """
    try:
        normalized_iocs = [normalize_ioc(ioc) for ioc in iocs]
        num_iocs = len(normalized_iocs)
        similarity_data = []

        for i in range(num_iocs):
            for j in range(i + 1, num_iocs):  # Avoid comparing IOCs with themselves and duplicates
                ioc1 = normalized_iocs[i]
                ioc2 = normalized_iocs[j]

                if similarity_metric == "jaccard":
                    set1 = set(ioc1)
                    set2 = set(ioc2)
                    similarity_score = jaccard_similarity(set1, set2)
                elif similarity_metric == "levenshtein":
                    distance = levenshtein_distance(ioc1, ioc2)
                    max_length = max(len(ioc1), len(ioc2))
                    similarity_score = 1 - (distance / max_length) if max_length > 0 else 1.0 # Ensure no division by zero

                else:
                    raise ValueError("Invalid similarity metric. Choose 'jaccard' or 'levenshtein'.")

                if similarity_score >= threshold:
                    similarity_data.append({
                        "IOC1": iocs[i],  #Original IOC
                        "IOC2": iocs[j], #Original IOC
                        "Normalized_IOC1": ioc1,
                        "Normalized_IOC2": ioc2,
                        "Similarity": similarity_score,
                        "Metric": similarity_metric
                    })

        df = pd.DataFrame(similarity_data)
        return df

    except ValueError as ve:
        logging.error(f"ValueError in calculate_similarity: {ve}")
        return pd.DataFrame() # Return empty DataFrame on error
    except Exception as e:
        logging.error(f"Error calculating similarity: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.

    Returns:
        argparse.ArgumentParser: The argument parser object.
    """
    parser = argparse.ArgumentParser(description="tit-IOC-Similarity-Analyzer: Calculates the similarity between IOCs.")
    parser.add_argument("-i", "--iocs", nargs='+', required=True, help="A list of IOCs to analyze.")
    parser.add_argument("-m", "--metric", choices=["jaccard", "levenshtein"], default="jaccard", help="The similarity metric to use (jaccard or levenshtein). Default: jaccard")
    parser.add_argument("-t", "--threshold", type=float, default=0.8, help="The similarity threshold (0.0-1.0). Default: 0.8")
    parser.add_argument("-o", "--output", help="Output file to save results (CSV format).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    return parser

def main():
    """
    The main function of the tool.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    iocs = args.iocs

    # Input validation for threshold
    if not 0.0 <= args.threshold <= 1.0:
        logging.error("Threshold must be between 0.0 and 1.0")
        sys.exit(1)

    try:
        similarity_df = calculate_similarity(iocs, args.metric, args.threshold)

        if similarity_df.empty:
            print("No similar IOCs found above the specified threshold.")
        else:
            print(tabulate(similarity_df, headers="keys", tablefmt="grid"))

            if args.output:
                try:
                    similarity_df.to_csv(args.output, index=False)
                    print(f"\nResults saved to: {args.output}")
                except Exception as e:
                    logging.error(f"Error saving results to file: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()