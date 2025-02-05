from rest_framework.test import APITestCase
from chat.models import Document  # Assurez-vous que le modèle Document est bien importé
from chat.serializers import DocumentSerializer
from datetime import datetime
from django.utils.timezone import make_aware

class DocumentSerializerTest(APITestCase):
    def setUp(self):
        # Utiliser datetime pour éviter les erreurs de format
        self.document_data = {
            'name': 'Test Document',
            'file_type': 'pdf',
            'upload_date': make_aware(datetime(2025, 2, 4, 10, 0, 0)),
        }

        # Crée un Document instance pour les tests
        self.document = Document.objects.create(**self.document_data)

    def test_document_serializer_valid_data(self):
        # Sérialiser l'objet Document
        serializer = DocumentSerializer(self.document)
        data = serializer.data

        # Vérifier que les champs sont bien présents dans les données sérialisées
        self.assertEqual(set(data.keys()), {'id', 'name', 'file_type', 'upload_date'})
        self.assertEqual(data['name'], self.document.name)
        self.assertEqual(data['file_type'], self.document.file_type)
        self.assertEqual(data['upload_date'], self.document.upload_date.isoformat(timespec='seconds'))

    def test_document_serializer_invalid_data(self):
        # Tester la désérialisation avec des données invalides
        invalid_data = {
            'name': '',  # Le nom ne doit pas être vide
            'file_type': 'txt',  # Ce test est valide si 'txt' est une valeur acceptée
            'upload_date': 'invalid-date-format',  # Mauvais format de date
        }

        # Créer une instance de serializer avec des données invalides
        serializer = DocumentSerializer(data=invalid_data)

        # Vérifier si la validation échoue
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)  # Le champ 'name' est requis
        self.assertTrue('upload_date' in serializer.errors or 'non_field_errors' in serializer.errors)

    def test_document_serializer_create(self):
        # Tester la création d'un Document à partir des données désérialisées
        valid_data = {
            'name': 'Another Test Document',
            'file_type': 'docx',
            'upload_date': datetime(2025, 2, 4, 11, 0, 0).isoformat(),
        }

        # Créer un serializer avec les données valides
        serializer = DocumentSerializer(data=valid_data)

        # Vérifier si la sérialisation est valide
        self.assertTrue(serializer.is_valid())

        # Sauvegarder l'objet si les données sont valides
        document_instance = serializer.save()

        # Vérifier que l'objet est bien créé
        self.assertEqual(document_instance.name, valid_data['name'])
        self.assertEqual(document_instance.file_type, valid_data['file_type'])
        self.assertEqual(document_instance.upload_date.isoformat(timespec='seconds'), valid_data['upload_date'])
