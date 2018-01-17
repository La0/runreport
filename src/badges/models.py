from django.db import models
from django.utils import timezone
from django.db.utils import IntegrityError
from django.conf import settings
from PIL import Image, ImageOps, ImageDraw
from helpers import nameize
import hashlib
import vinaigrette
import os


class BadgeCategory(models.Model):
    '''
    Group badges by categories
    '''
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name

    def get_user_value(self, user):
        '''
        Get the user value for each category
        '''
        from sport.models import SportSession
        sessions = SportSession.objects.filter(day__week__user=user)

        if self.name == 'distance':
            # Sum of distance for user
            agg = sessions.aggregate(total=models.Sum('distance'))
            return agg['total']

        if self.name == 'denivele':
            # Sum of elevation for user
            agg = sessions.aggregate(total=models.Sum('elevation_gain'))
            return agg['total']

        if self.name == 'time':
            # Sum of time for user, as days
            agg = sessions.aggregate(total=models.Sum('time'))
            nb = agg['total']
            return nb and nb.days or 0

        if self.name == 'age':
            # Membership age in years
            diff = timezone.now() - user.date_joined
            return diff.days / 365  # cast to int

        if self.name == 'trainer':
            # Nb of trained athletes, in all clubs
            from club.models import ClubMembership
            return ClubMembership.objects.filter(trainers=user).count()

        return 0.0

    def find_badges(self, user, save=False):
        '''
        Find the best badges for an user
        Optionally save them
        '''
        # Search badges
        val = self.get_user_value(user)
        if not val:
            return None, None
        badges = self.badges.filter(value__lte=val)

        # Save badges
        added_badges = []
        if save:
            for b in badges:
                try:
                    BadgeUser.objects.create(user=user, badge=b)
                    added_badges.append(b)
                except IntegrityError:
                    pass  # If badge already exist

        return badges, added_badges


# Translation
vinaigrette.register(BadgeCategory, ['name', ])


def badge_image_path(instance, filename):
    return instance.build_image_path()


class Badge(models.Model):
    '''
    Badge earned by users after some events
    '''
    name = models.CharField(max_length=250, unique=True)
    value = models.CharField(max_length=250, blank=True, null=True)
    category = models.ForeignKey(BadgeCategory, related_name='badges')
    position = models.IntegerField()
    image = models.ImageField(
        upload_to=badge_image_path,
        default='badges/default.png')
    users = models.ManyToManyField(
        'users.Athlete',
        through='badges.BadgeUser',
        related_name='badges')

    def __str__(self):
        return u'%s : %s #%d' % (self.category.name, self.name, self.position)

    class Meta:
        ordering = ('position', )
        unique_together = (
            ('category', 'position'),
        )

    def build_image_path(self):
        '''
        Helper to build the image path for the badge
        '''
        h = hashlib.md5(
            '%s:%s:%s' %
            (self.pk,
             settings.SECRET_KEY,
             timezone.now())).hexdigest()
        return 'badges/%s.%s.%s.png' % (self.category.name,
                                        self.position, h[0:6])

    def build_image(self):
        '''
        Build a Badge image, using a source
        Cropped as a centered circle, with
        custom background
        '''

        # Files
        img_dir = os.path.join(settings.BASE_DIR, 'badges/images')
        bg_path = os.path.join(img_dir, 'background.png')
        if not os.path.exists(bg_path):
            raise Exception('Missing background %s' % bg_path)

        src_path = os.path.join(img_dir, '%s/%s.jpg' %
                                (self.category.name, nameize(self.name)))
        if not os.path.exists(src_path):
            raise Exception('Missing source image %s' % src_path)

        # Images config
        img_size = (360, 360)
        mask_size = (300, 300)

        # Draw mask
        mask = Image.new('L', img_size, 0)
        draw = ImageDraw.Draw(mask)
        x = (img_size[0] - mask_size[0]) / 2.0
        y = (img_size[1] - mask_size[1]) / 2.0
        draw.ellipse((x, y, mask_size[0] + x, mask_size[1] + y), fill=255)

        # Apply mask to image
        src = Image.open(src_path)
        circle = ImageOps.fit(src, mask.size, centering=(0.5, 0.5))
        circle.putalpha(mask)

        # Composite mask & background
        bg = Image.open(bg_path)
        output = Image.alpha_composite(bg, circle)
        output_path = self.build_image_path()
        output.save(os.path.join(settings.MEDIA_ROOT, output_path))

        # Save new image reference
        self.image = output_path
        self.save()

        return output


# Translation
vinaigrette.register(Badge, ['name', ])


class BadgeUser(models.Model):
    '''
    Link between a badge & user
    '''
    badge = models.ForeignKey(Badge)
    user = models.ForeignKey('users.Athlete')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('badge', 'user'),
        )
