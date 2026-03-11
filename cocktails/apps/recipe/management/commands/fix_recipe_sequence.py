from django.core.management.base import BaseCommand
from django.db import connection
from apps.recipe.models import Recipe, RecipeIngredient
import logging

logger = logging.getLogger(__name__)


class SequenceTable:
    """Class to handle sequence operations for different tables"""
    
    def __init__(self, table_name, model_name, display_name):
        self.table_name = table_name
        self.model_name = model_name
        self.display_name = display_name


class Command(BaseCommand):
    help = 'Fix PostgreSQL sequences for Recipe-related tables to prevent UniqueViolation/IntegrityError errors'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
        parser.add_argument(
            '--table',
            type=str,
            choices=['recipe', 'ingredient', 'all'],
            default='all',
            help='Which table to fix: recipe, ingredient, or all (default: all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        table_filter = options['table']
        
        self.stdout.write(
            self.style.WARNING('🔧 PostgreSQL Recipe System Sequence Fix Utility')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('📋 DRY RUN MODE - No changes will be made')
            )

        # Define tables to process
        tables_to_process = []
        
        if table_filter in ['recipe', 'all']:
            tables_to_process.append(
                SequenceTable('recipe_recipe', 'Recipe', '🍸 Recipe')
            )
        
        if table_filter in ['ingredient', 'all']:
            tables_to_process.append(
                SequenceTable('recipe_recipeingredient', 'RecipeIngredient', '🥃 RecipeIngredient')
            )

        self.stdout.write(f'📋 Processing {len(tables_to_process)} table(s): {table_filter}')

        try:
            with connection.cursor() as cursor:
                overall_conflicts_detected = False
                results = {}

                # Process each table
                for table_config in tables_to_process:
                    self.stdout.write(
                        self.style.HTTP_INFO(f'\n{table_config.display_name} Table Processing')
                    )
                    
                    conflict_detected = self._process_table(
                        cursor, table_config, dry_run, verbose
                    )
                    
                    results[table_config.display_name] = {
                        'conflict_detected': conflict_detected,
                        'table_name': table_config.table_name
                    }
                    
                    if conflict_detected:
                        overall_conflicts_detected = True

                # Final summary report
                self._generate_final_report(results, dry_run, overall_conflicts_detected)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during sequence fix: {str(e)}')
            )
            if verbose:
                import traceback
                self.stdout.write(traceback.format_exc())
            raise

        self.stdout.write('🏁 Recipe System Sequence Fix command completed')

    def _process_table(self, cursor, table_config, dry_run, verbose):
        """Process a single table sequence"""
        
        # STEP 1: Диагностика текущего состояния
        self.stdout.write(f'🔍 Step 1: Diagnosing {table_config.display_name} state...')
        
        # Проверяем максимальный ID в таблице
        cursor.execute(f"SELECT MAX(id) as max_id FROM {table_config.table_name};")
        max_id_result = cursor.fetchone()
        max_id = max_id_result[0] if max_id_result[0] else 0
        
        # Проверяем количество записей
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_config.table_name};")
        count = cursor.fetchone()[0]
        
        self.stdout.write(f'📊 Records in {table_config.table_name}: {count}')
        self.stdout.write(f'📈 Maximum ID in table: {max_id}')
        
        # Проверяем текущее состояние sequence
        sequence_name = f"pg_get_serial_sequence('{table_config.table_name}', 'id')"
        conflict_detected = False
        
        try:
            cursor.execute(f"SELECT currval({sequence_name}) as current_seq;")
            current_seq = cursor.fetchone()[0]
            self.stdout.write(f'🔢 Current sequence value: {current_seq}')
            
            # Проверяем конфликт
            if current_seq <= max_id:
                self.stdout.write(
                    self.style.ERROR(f'⚠️ SEQUENCE CONFLICT DETECTED!')
                )
                self.stdout.write(
                    self.style.ERROR(f'   Sequence value ({current_seq}) <= Max ID ({max_id})')
                )
                conflict_detected = True
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ No sequence conflict detected')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Cannot get currval (sequence may not be used): {str(e)}')
            )
            # Попробуем получить последнее значение sequence
            try:
                sequence_table_name = f"{table_config.table_name}_id_seq"
                cursor.execute(f"SELECT last_value FROM {sequence_table_name};")
                last_value = cursor.fetchone()[0]
                self.stdout.write(f'📊 Last sequence value: {last_value}')
                
                if last_value <= max_id:
                    conflict_detected = True
                    self.stdout.write(
                        self.style.ERROR(f'⚠️ SEQUENCE CONFLICT DETECTED!')
                    )
                    self.stdout.write(
                        self.style.ERROR(f'   Last sequence value ({last_value}) <= Max ID ({max_id})')
                    )
                else:
                    conflict_detected = False
                    self.stdout.write(
                        self.style.SUCCESS('✅ No sequence conflict detected')
                    )
            except Exception as e2:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error accessing sequence: {str(e2)}')
                )
                # Assume conflict if we can't check
                conflict_detected = True

        # STEP 2: Исправление sequence если нужно
        if conflict_detected:
            self.stdout.write(f'🛠️ Step 2: Fixing {table_config.display_name} sequence...')
            
            # Вычисляем новое значение sequence
            new_sequence_value = max_id + 1
            self.stdout.write(f'🎯 Setting sequence to: {new_sequence_value}')
            
            if not dry_run:
                # Применяем исправление
                cursor.execute(
                    f"SELECT setval({sequence_name}, %s);",
                    [new_sequence_value]
                )
                
                # Проверяем результат
                cursor.execute(f"SELECT currval({sequence_name});")
                updated_seq = cursor.fetchone()[0]
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Sequence updated successfully to: {updated_seq}')
                )
                
                # STEP 3: Тест создания записи
                if verbose:
                    self.stdout.write(f'🧪 Step 3: Testing {table_config.display_name} sequence...')
                    
                    # Имитируем создание без реального сохранения
                    cursor.execute(f"SELECT nextval({sequence_name});")
                    next_id = cursor.fetchone()[0]
                    self.stdout.write(f'🔢 Next available ID would be: {next_id}')
                    
                    # Возвращаем sequence обратно (rollback nextval)
                    cursor.execute(
                        f"SELECT setval({sequence_name}, %s);",
                        [new_sequence_value]
                    )
                    
                    if next_id > max_id:
                        self.stdout.write(
                            self.style.SUCCESS('✅ Sequence test PASSED - no conflicts expected')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR('❌ Sequence test FAILED - conflicts may still occur')
                        )
            else:
                self.stdout.write(
                    self.style.WARNING(f'📋 DRY RUN: Would set sequence to {new_sequence_value}')
                )
        else:
            self.stdout.write(f'✅ Step 2: No {table_config.display_name} sequence fix needed')

        return conflict_detected

    def _generate_final_report(self, results, dry_run, overall_conflicts_detected):
        """Generate final summary report"""
        
        self.stdout.write('\n📋 FINAL SUMMARY REPORT')
        self.stdout.write('=' * 50)
        
        # Per-table results
        for display_name, result in results.items():
            status = "⚠️ CONFLICT DETECTED" if result['conflict_detected'] else "✅ OK"
            self.stdout.write(f'{display_name}: {status}')
        
        # Overall status
        if not dry_run and overall_conflicts_detected:
            self.stdout.write(
                self.style.SUCCESS('\n🎉 RECIPE SYSTEM SEQUENCE FIX COMPLETED')
            )
            self.stdout.write('📝 Summary of changes:')
            fixed_tables = [name for name, result in results.items() if result['conflict_detected']]
            for table_name in fixed_tables:
                self.stdout.write(f'   - {table_name} sequence synchronized')
            self.stdout.write('   - UniqueViolation/IntegrityError errors should be resolved')
            
        elif dry_run and overall_conflicts_detected:
            self.stdout.write(
                self.style.WARNING('\n📋 DRY RUN COMPLETED - Run without --dry-run to apply fixes')
            )
            conflicted_tables = [name for name, result in results.items() if result['conflict_detected']]
            self.stdout.write('Tables requiring fixes:')
            for table_name in conflicted_tables:
                self.stdout.write(f'   - {table_name}')
                
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✅ ALL SEQUENCE STATUS: OK - No action needed')
            )

        # Usage examples
        if overall_conflicts_detected:
            self.stdout.write('\n�� Usage Examples:')
            self.stdout.write('   Fix all tables:     python manage.py fix_recipe_sequence')
            self.stdout.write('   Fix recipe only:    python manage.py fix_recipe_sequence --table recipe')
            self.stdout.write('   Fix ingredients:    python manage.py fix_recipe_sequence --table ingredient')
            self.stdout.write('   Dry run first:      python manage.py fix_recipe_sequence --dry-run')
