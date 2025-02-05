import pytest
from rest_framework.test import APITestCase
from chat.models import Document  # Assurez-vous que le modèle Document est bien importé
from chat.serializers import DocumentSerializer
from datetime import datetime, timezone, timedelta
from django.utils.timezone import make_aware, is_naive
import uuid

class DocumentSerializerTest(APITestCase):
    def setUp(self):
        # Utiliser datetime pour éviter les erreurs de format et forcer UTC
        self.document_data = {
            'name': 'Test Document',
            'file_type': 'pdf',
            'upload_date': make_aware(datetime(2025, 2, 4, 10, 0, 0)).astimezone(timezone.utc),
            'chroma_id': str(uuid.uuid4()),  # Générer un chroma_id unique
        }

        # Crée un Document instance pour les tests
        self.document = Document.objects.create(**self.document_data)

    def test_document_serializer_valid_data(self):
        # Sérialiser l'objet Document
        serializer = DocumentSerializer(self.document)
        data = serializer.data

        # Vérifier que les champs sont bien présents dans les données sérialisées
        expected_fields = {'id', 'name', 'file_type', 'upload_date'}
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertEqual(data['name'], self.document.name)
        self.assertEqual(data['file_type'], self.document.file_type)
        self.assertEqual(data['upload_date'].replace("Z", "+00:00"), self.document.upload_date.isoformat())

    def test_document_serializer_invalid_data(self):
        # Tester la désérialisation avec des données invalides
        invalid_data = {
            'name': '',  # Le nom ne doit pas être vide
            'file_type': 'txt',  # Ce test est valide si 'txt' est une valeur acceptée
            'upload_date': 'invalid-date-format',  # Mauvais format de date
            'chroma_id': str(uuid.uuid4()),
        }

        # Créer une instance de serializer avec des données invalides
        serializer = DocumentSerializer(data=invalid_data)

        # Vérifier si la validation échoue
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)  # Le champ 'name' est requis

    def test_document_serializer_create(self):
        # Tester la création d'un Document à partir des données désérialisées
        upload_date = datetime(2025, 2, 4, 11, 0, 0, tzinfo=timezone.utc)  # Assurer que la date est bien en UTC

        valid_data = {
            'name': 'Another Test Document',
            'file_type': 'docx',
            'upload_date': make_aware(datetime(2025, 2, 4, 10, 0, 0)).astimezone(timezone.utc),
            'chroma_id': str(uuid.uuid4()),  # Générer un chroma_id unique
        }
        document = Document.objects.create(**valid_data)
        serializer = DocumentSerializer(document)
        data = serializer.data
        # Créer un serializer avec les données valides
        serializer = DocumentSerializer(data=valid_data)

        # Vérifier si la sérialisation est valide
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # Sauvegarder l'objet si les données sont valides
        document_instance = serializer.save()

        # Normaliser la date attendue en UTC
        expected_date = upload_date.replace(microsecond=0).isoformat()
        saved_date = document_instance.upload_date.replace(microsecond=0).isoformat()

        # Vérifier que l'objet est bien créé
        self.assertEqual(document_instance.name, valid_data['name'])
        self.assertEqual(document_instance.file_type, valid_data['file_type'])
        self.assertEqual(data['upload_date'].replace("Z", "+00:00"), self.document.upload_date.isoformat())