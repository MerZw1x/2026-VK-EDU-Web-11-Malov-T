from array import array
from math import gcd
from random import Random
from time import monotonic
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int)
        parser.add_argument("--batch-size", type=int, default=1000)

    def handle(self, *args, **options):
        ratio = options["ratio"]
        batch_size = options["batch_size"]
        if ratio < 2:
            raise CommandError("ratio должен быть не меньше 2")
        if batch_size < 1:
            raise CommandError("Размер пачки должен быть положительным")

        fake = Faker("ru_RU")
        tag_fake = Faker("en_US")
        rng = Random()
        run_id = uuid4().hex[:12]
        started = monotonic()
        paragraphs = [fake.paragraph(nb_sentences=5) for _ in range(256)]

        with transaction.atomic():
            user_ids = self.create_users(ratio, batch_size, run_id, fake)
            self.report("пользователей", len(user_ids))
            self.create_profiles(user_ids, batch_size, fake)
            self.report("профилей", len(user_ids))
            tag_ids = self.create_tags(ratio, batch_size, run_id, tag_fake)
            self.report("тегов", len(tag_ids))
            question_ids = self.create_questions(
                ratio * 10, user_ids, batch_size, fake, paragraphs, rng,
            )
            self.report("вопросов", len(question_ids))
            tag_count = self.create_question_tags(question_ids, tag_ids, batch_size, rng)
            self.report("связей вопрос–тег", tag_count)
            answer_ids = self.create_answers(
                ratio * 100, question_ids, user_ids, batch_size, paragraphs, rng,
            )
            self.report("ответов", len(answer_ids))

            total_votes = ratio * 200
            question_votes = min(total_votes // 2, len(user_ids) * len(question_ids))
            answer_votes = total_votes - question_votes
            self.create_votes(
                QuestionLike, "question", Question, question_ids, user_ids,
                question_votes, batch_size, rng,
            )
            self.report("оценок вопросов", question_votes)
            self.create_votes(
                AnswerLike, "answer", Answer, answer_ids, user_ids,
                answer_votes, batch_size, rng,
            )
            self.report("оценок ответов", answer_votes)

        self.stdout.write(self.style.SUCCESS(
            f"Готово: запуск {run_id}, {monotonic() - started:.1f} с. "
            "Все изменения сохранены."
        ))

    def report(self, entity, count):
        self.stdout.write(f"Создано {entity}: {count}")

    def insert(self, model, objects, batch_size, collect_ids=True):
        ids = array("q")
        batch = []
        for obj in objects:
            batch.append(obj)
            if len(batch) == batch_size:
                created = model.objects.bulk_create(batch, batch_size=batch_size)
                if collect_ids:
                    ids.extend(obj.pk for obj in created)
                batch = []
        if batch:
            created = model.objects.bulk_create(batch, batch_size=batch_size)
            if collect_ids:
                ids.extend(obj.pk for obj in created)
        return ids

    def create_users(self, count, batch_size, run_id, fake):
        user_model = get_user_model()

        def objects():
            for index in range(count):
                username = f"user_{run_id}_{index}"
                user = user_model(
                    username=username,
                    email=f"{username}@example.com",
                    first_name=fake.first_name()[:150],
                    last_name=fake.last_name()[:150],
                )
                user.set_unusable_password()
                yield user

        return self.insert(user_model, objects(), batch_size)

    def create_profiles(self, user_ids, batch_size, fake):
        objects = (
            Profile(user_id=user_id, nickname=fake.name()[:40])
            for user_id in user_ids
        )
        self.insert(Profile, objects, batch_size, collect_ids=False)

    def create_tags(self, count, batch_size, run_id, fake):
        def objects():
            for index in range(count):
                name = f"{fake.word()[:15]}-{run_id}-{index}"
                yield Tag(name=name, slug=name.lower())

        return self.insert(Tag, objects(), batch_size)

    def create_questions(self, count, user_ids, batch_size, fake, paragraphs, rng):
        objects = (
            Question(
                author_id=rng.choice(user_ids),
                title=fake.sentence(nb_words=10)[:255],
                text="\n\n".join(rng.sample(paragraphs, 3))[:10000],
            )
            for _ in range(count)
        )
        return self.insert(Question, objects, batch_size)

    def create_question_tags(self, question_ids, tag_ids, batch_size, rng):
        through = Question.tags.through
        count = 0

        def objects():
            nonlocal count
            for question_id in question_ids:
                size = rng.randint(1, min(3, len(tag_ids)))
                for tag_id in rng.sample(tag_ids, size):
                    count += 1
                    yield through(question_id=question_id, tag_id=tag_id)

        self.insert(through, objects(), batch_size, collect_ids=False)
        return count

    def create_answers(self, count, question_ids, user_ids, batch_size, paragraphs, rng):
        def objects():
            for index in range(count):
                question_index = index % len(question_ids)
                yield Answer(
                    author_id=rng.choice(user_ids),
                    question_id=question_ids[question_index],
                    text="\n\n".join(rng.sample(paragraphs, 2))[:5000],
                    is_correct=index < len(question_ids) and question_index % 2 == 0,
                )

        return self.insert(Answer, objects(), batch_size)

    def create_votes(
        self, vote_model, field, target_model, target_ids, user_ids,
        count, batch_size, rng,
    ):
        capacity = len(target_ids) * len(user_ids)
        if count > capacity:
            raise CommandError("Недостаточно уникальных пар для генерации оценок")

        step = rng.randrange(1, capacity)
        while gcd(step, capacity) != 1:
            step = rng.randrange(1, capacity)
        offset = rng.randrange(capacity)
        ratings = array("i", [0]) * len(target_ids)

        def objects():
            for index in range(count):
                pair = (offset + index * step) % capacity
                user_index, target_index = divmod(pair, len(target_ids))
                value = 1 if rng.random() < 0.75 else -1
                ratings[target_index] += value
                yield vote_model(
                    user_id=user_ids[user_index],
                    **{f"{field}_id": target_ids[target_index]},
                    value=value,
                )

        self.insert(vote_model, objects(), batch_size, collect_ids=False)
        for start in range(0, len(target_ids), batch_size):
            targets = [
                target_model(pk=target_ids[index], rating=ratings[index])
                for index in range(start, min(start + batch_size, len(target_ids)))
            ]
            target_model.objects.bulk_update(targets, ["rating"], batch_size=batch_size)
