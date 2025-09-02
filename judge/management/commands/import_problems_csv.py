from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from judge.bulk_import_forms import CSVImportForm
from judge.models import Problem
import sys


class Command(BaseCommand):
    help = '從 CSV 文件匯入題目'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='CSV 文件路徑')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='僅驗證 CSV 文件，不實際創建題目',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        dry_run = options['dry_run']

        try:
            with open(csv_file_path, 'rb') as f:
                # 創建一個模擬的文件對象
                from django.core.files.uploadedfile import SimpleUploadedFile
                csv_file = SimpleUploadedFile(
                    name=csv_file_path,
                    content=f.read(),
                    content_type='text/csv'
                )

                form = CSVImportForm({'csv_file': csv_file})
                form.files['csv_file'] = csv_file

                if not form.is_valid():
                    for field, errors in form.errors.items():
                        for error in errors:
                            self.stdout.write(
                                self.style.ERROR(f'{field}: {error}')
                            )
                    raise CommandError('CSV 文件驗證失敗')

                problems_to_create = form.process_csv()
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(f'驗證成功！將創建 {len(problems_to_create)} 個題目')
                    )
                    for problem_data in problems_to_create:
                        self.stdout.write(f"- {problem_data['code']}: {problem_data['name']}")
                    return

                # 實際創建題目
                created_count = 0
                with transaction.atomic():
                    for problem_data in problems_to_create:
                        self._create_problem(problem_data)
                        created_count += 1
                        self.stdout.write(f"已創建題目: {problem_data['code']}")

                self.stdout.write(
                    self.style.SUCCESS(f'成功創建了 {created_count} 個題目')
                )

        except FileNotFoundError:
            raise CommandError(f'找不到文件: {csv_file_path}')
        except Exception as e:
            raise CommandError(f'處理文件時發生錯誤: {str(e)}')

    def _create_problem(self, problem_data):
        """創建單個題目"""
        # 提取多對多關係字段
        types = problem_data.pop('types', [])
        authors = problem_data.pop('authors', [])
        allowed_languages = problem_data.pop('allowed_languages', [])

        # 創建題目
        problem = Problem.objects.create(**problem_data)

        # 設置多對多關係
        if types:
            problem.types.set(types)
        if authors:
            problem.authors.set(authors)
        if allowed_languages:
            problem.allowed_languages.set(allowed_languages)
        else:
            # 如果沒有指定語言，設置所有可用語言
            from judge.models import Language
            problem.allowed_languages.set(Language.objects.all())

        return problem
