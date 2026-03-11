# Исправленная логика для многословного поиска
        # For multiple words - use more strict logic to avoid too many results
        # First try exact phrase search, fallback to selective morphology
        
        # Try exact phrase search first (without morphology)
        exact_phrase = ' '.join(value_list)
        exact_results = set()
        
        # Search for exact phrase in all fields
        exact_regular = queryset.filter(
            Q(title__icontains=exact_phrase) |
            Q(description__icontains=exact_phrase) |
            Q(recipe_ingredients__ingredient__name__icontains=exact_phrase)
        ).values_list('id', flat=True)
        exact_results.update(exact_regular)
        
        # Search for exact phrase in instructions
        try:
            exact_instruction = queryset.extra(
                where=["instruction IS NOT NULL AND array_to_string(ARRAY(SELECT value FROM jsonb_each_text(instruction)), ' ') ILIKE %s"],
                params=[f'%{exact_phrase}%']
            ).values_list('id', flat=True)
            exact_results.update(exact_instruction)
        except Exception:
            exact_instruction = queryset.filter(instruction__icontains=exact_phrase).values_list('id', flat=True)
            exact_results.update(exact_instruction)
        
        # If exact phrase found results, return them (more precise)
        if len(exact_results) > 0:
            return queryset.filter(id__in=exact_results).distinct()
        
        # If no exact results, fall back to morphological word-by-word search
        # But use morphology only for verbs to maintain precision
        filtered_queryset = queryset
        
        for word in value_list:
            word_ids = set()
            
            # Use morphology only for known culinary verbs, exact search for other words
            if word.lower() in MORPHOLOGY_MAP and word.lower() != MORPHOLOGY_MAP[word.lower()]:
                # This is a morphological form (like "смешай" -> "смешать")
                word_variants = get_morphological_variants(word)
            else:
                # Use exact word for nouns, adjectives, and already correct forms
                word_variants = [word]
            
            for variant in word_variants:
                # Get IDs of recipes matching this variant
                regular_ids = filtered_queryset.filter(
                    Q(title__icontains=variant) |
                    Q(description__icontains=variant) |
                    Q(recipe_ingredients__ingredient__name__icontains=variant)
                ).values_list('id', flat=True)
                word_ids.update(regular_ids)
                
                # Search in instructions
                try:
                    instruction_ids = filtered_queryset.extra(
                        where=["instruction IS NOT NULL AND array_to_string(ARRAY(SELECT value FROM jsonb_each_text(instruction)), ' ') ILIKE %s"],
                        params=[f'%{variant}%']
                    ).values_list('id', flat=True)
                    word_ids.update(instruction_ids)
                except Exception:
                    instruction_ids = filtered_queryset.filter(instruction__icontains=variant).values_list('id', flat=True)
                    word_ids.update(instruction_ids)
            
            # Each word must match (AND logic)
            filtered_queryset = filtered_queryset.filter(id__in=word_ids).distinct()
        
        return filtered_queryset
