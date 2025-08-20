from mongoengine import (
    Document,
    StringField,
    IntField,
    ListField,
    EmailField,
    EmbeddedDocument,
    EmbeddedDocumentField,
)


class Socials(EmbeddedDocument):
    githubUrl = StringField(default="")
    linkedInUrl = StringField(default="")
    leetcodeUrl = StringField(default="")
    xUrl = StringField(default="")

class User(Document):
    name = StringField(required=True)
    email = EmailField()
    socials = EmbeddedDocumentField(Socials, default=Socials)


# u = User(name="Alice", email="alice@example.com", socials=Socials(
#     githubUrl="https://github.com/alice",
#     linkedInUrl="https://linkedin.com/in/alice",
#     leetcodeUrl="https://leetcode.com/alice",
#     xUrl="https://x.com/alice"
# ))
# u.save()
